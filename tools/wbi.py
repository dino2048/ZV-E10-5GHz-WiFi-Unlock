"""Guarded WBI invalidation, using only the Sony utility tested on known systems 2.02 and 2.03.
No general block writer or automatic restore is exposed.
"""
import hashlib
import json
import os
import re
import uuid
from pathlib import Path

SIZE = 60 * 1024 * 1024
DEVICE = '/dev/nflasha5'
TOOL_HASH = 'f2a5b27a0c11d55a612d61e61e82c55278efb744052ecb8ec2cbbd8851d0ea6e'
CONFIG = (b'# start address,size,type,flag\n'
          b'0x00010000,0x007F0000,0x00000001,0xFFFFFFFF\n'
          b'0x00800000,0x01400000,0x00000001,0xFFFFFFFF\n'
          b'0x01C00000,0x03000000,0x00000001,0xFFFFFFFF\n'
          b'0x04C00000,0x00C00000,0x00000000,0xFFFFFFFF\n'
          b'0x05800000,0x03C00000,0x00000002,0xFFFFFFFF\n')
CONFIG_HASH = '9bb1cba13c10ce88bd88d054dc49a823b3b1409ce6dfbeaeaa180f31d22744a8'
SYSTEMS = {
    b'30110_05.2025031501': ('2.02', 21305456, 'bc0deb2f0e94218752e42ce6f5a3576d7456971eb63fbde705ffbd9b3a7fdeea'),
    b'30110_06.2026060501': ('2.03', 21305528, 'cfdc59b94fa56116e9d99154ca03a2c1aaf6039dd272679b78b0b76e21c722ac'),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def validate_tool(data):
    if len(data) != 6200 or sha(data) != TOOL_HASH:
        raise ValueError('Unknown Sony ud_wbi_drop.elf size/hash; STOP')


def validate_partition(partitions, geometry, node=None):
    rows = [r.split() for r in partitions.splitlines() if r.split() and r.split()[-1] == 'nflasha5']
    if len(rows) != 1 or len(rows[0]) != 4 or rows[0][2] != '61440':
        raise ValueError('WBI partition missing, ambiguous or wrong size; STOP')
    major, minor = rows[0][:2]
    # sysfs ties the name to the real block device and verifies sector geometry.
    if geometry.split() != [major + ':' + minor, '180224', '122880']:
        raise ValueError('WBI device identity/start/size mismatch; STOP')
    if node is not None and not re.search(r'^b\S*\s+.*\s' + re.escape(major) + r',\s*' + re.escape(minor) + r'\s.* /dev/nflasha5\s*$', node.strip()):
        raise ValueError('WBI block node major/minor mismatch; STOP')
    return {'device': DEVICE, 'dev': major + ':' + minor, 'start': 0x05800000, 'bytes': SIZE}


def identity(camera, ops, folder, require_patch=True):
    """Verify the camera/WBI identity. ``require_patch`` gates the write path.

    A read-only status query only needs the system, model and partition checks;
    requiring the patched library there made the WBI state unreadable on a
    factory or already-reverted camera.
    """
    evidence = {}
    try:
        system = ops.check_firmware(camera)
        if system not in SYSTEMS:
            raise ValueError('Unknown camera system fingerprint')
        label, model_size, model_hash = SYSTEMS[system]
        evidence['system'] = system.decode('ascii')
        model_library = ops.read_file(camera, '/usr/lib/libObj.so')
        evidence['libObj'] = {'bytes': len(model_library), 'sha256': sha(model_library)}
        if len(model_library) != model_size or sha(model_library) != model_hash:
            raise ValueError('ZV-E10 model/system library fingerprint mismatch; STOP')
        if require_patch:
            target = ops.read_file(camera, ops.TARGET)
            evidence['CautionConfig'] = {'bytes': len(target), 'sha256': sha(target)}
            ops.verify(target, ops.PATCHED)
            values = {hex(k): ops.backup_properties.dispatch(
                camera, {'action': 'backup-read', 'id': hex(k)}, folder, False)['value'] for k in ops.KEYS}
            if any(not isinstance(v, str) or not re.fullmatch(r'[0-9a-fA-F]{2}', v)
                   for v in values.values()):
                raise ValueError('Malformed Backup-property readback; STOP')
            values = {key: value.lower() for key, value in values.items()}
            evidence['backup'] = values
            if values[hex(ops.KEYS[0])] != '01':
                raise ValueError('WBI menu recovery requires the frequency-menu property enabled; STOP')
        evidence['partitions'] = ops.run(camera, 'busybox cat /proc/partitions')
        evidence['geometry'] = ops.run(camera, 'busybox cat /sys/class/block/nflasha5/dev /sys/class/block/nflasha5/start /sys/class/block/nflasha5/size')
        ops.run(camera, 'test -b /dev/nflasha5 && test ! -L /dev/nflasha5')
        evidence['node'] = ops.run(camera, 'busybox ls -l /dev/nflasha5')
        result = dict(validate_partition(evidence['partitions'], evidence['geometry'], evidence['node']), displayed_firmware=label)
        if require_patch:
            # WBI invalidation does not select or modify a region. Bind the
            # actual properties to preparation so every later identity check
            # rejects a changed configuration, regardless of the selected B/C.
            result['backup'] = values
        return result
    except Exception as exc:
        evidence['error'] = repr(exc)
        raise
    finally:
        ops.save_private(folder, 'wbi-identity-' + uuid.uuid4().hex + '.json',
                         (json.dumps(evidence, indent=2) + '\n').encode())


def read_partition(camera, folder, name, ops):
    """Bounded streaming toolkit backend read, preserving partial data on failure."""
    path = folder / name
    class Sink:
        size = 0
        def write(self, data):
            if self.size + len(data) > SIZE:
                raise RuntimeError('WBI read exceeds capacity; STOP')
            output.write(data)
            self.size += len(data)
    with path.open('xb') as output:
        path.chmod(0o600)
        ops.common.restore_owner(path)
        sink = Sink()
        ops.common.set_terminal_timeout(camera, 30000)
        status, _ = ops.common.read_path(camera, DEVICE, sink)
        output.flush()
        os.fsync(output.fileno())
    if status not in (0, 1) or sink.size != SIZE:
        raise RuntimeError('Incomplete WBI read; saved partial evidence: ' + str(path))
    return path.read_bytes()


def validate_state(data):
    if len(data) != SIZE:
        raise ValueError('Wrong full WBI size; STOP')
    if data[:512] == bytes(512):
        return 'already-invalid'
    if data[:4] != b'WBI1':
        raise ValueError('Unknown WBI header; no write')
    return 'valid'


def validate_backups(first, second):
    if len(first) != SIZE or len(second) != SIZE:
        raise ValueError('Wrong full WBI backup size; STOP')
    if sha(first) != sha(second) or first != second:
        raise ValueError('Double WBI backups differ; no write')
    return validate_state(first)


def validate_after(before, after):
    if len(before) != SIZE or len(after) != SIZE:
        raise RuntimeError('Wrong WBI readback size; STOP, preserve evidence')
    if after[:512] != bytes(512) or after[512:] != before[512:]:
        raise RuntimeError('WBI write differs outside expected first 512 bytes or header is not zero; STOP, no automatic restore')


def dispatch(camera, req, folder, allow_write, ops):
    token = uuid.uuid4().hex
    report = {'action': req['action'], 'token': token, 'write_attempted': False}
    prefix = 'wbi-' + token
    def record():
        # Each transaction gets a unique diagnostic file, including failures.
        ops.save_private(folder, prefix + '-result.json', (json.dumps(report, indent=2) + '\n').encode())
    try:
        if req['action'] == 'wbi-status':
            # Read-only: one partition read, no Sony tool, no token, no write.
            # Works in any library state so the WBI itself can be inspected.
            report['read_only'] = True
            report['identity'] = identity(camera, ops, folder, require_patch=False)
            data = read_partition(camera, folder, prefix + '-status.bin', ops)
            report['wbi_sha256'] = sha(data)
            report['status'] = validate_state(data)
            record()
            return report
        if req['action'] == 'wbi-prepare':
            if req.get('model') != 'ZV-E10' or req.get('displayed_firmware') not in ('2.02', '2.03'):
                raise ValueError('Owner must confirm first-generation ZV-E10 and displayed system 2.02/2.03')
            tool = Path(req['sony_tool']).read_bytes()
            validate_tool(tool)
            report['identity'] = identity(camera, ops, folder)
            if report['identity'].get('displayed_firmware', req['displayed_firmware']) != req['displayed_firmware']:
                raise ValueError('Displayed firmware differs from the checked system')
            first = read_partition(camera, folder, prefix + '-read1.bin', ops)
            second = read_partition(camera, folder, prefix + '-read2.bin', ops)
            report['backup_sha256'] = [sha(first), sha(second)]
            report['status'] = validate_backups(first, second)
            report['warning'] = 'Next action writes eMMC: invalidate ONLY the first 512 bytes of nflasha5. Keep both full backups; recovery is not automatic.'
            report['confirmation'] = 'INVALIDATE WBI ' + sha(first)
            record()
            return report
        if not allow_write:
            raise ValueError('WBI write requires --owner-authorized-write and separate explicit confirmation')
        prepared = req.get('prepared', '')
        if not re.fullmatch(r'[0-9a-f]{32}', prepared):
            raise ValueError('Invalid WBI preparation token')
        base = 'wbi-' + prepared
        previous = json.loads((folder / (base + '-result.json')).read_text())
        if previous.get('action') != 'wbi-prepare' or previous.get('status') != 'valid':
            raise ValueError('Preparation not valid or WBI already invalid; no write')
        if req.get('confirm_emmc_write') != previous['confirmation'] or req.get('recovery_ready') is not True:
            raise ValueError('Explain eMMC risk, obtain owner confirmation and verify recovery readiness first')
        tool = Path(req['sony_tool']).read_bytes()
        validate_tool(tool)
        report['identity'] = identity(camera, ops, folder)
        if report['identity'] != previous['identity']:
            raise ValueError('Device identity changed since preparation; STOP')
        first = (folder / (base + '-read1.bin')).read_bytes()
        second = (folder / (base + '-read2.bin')).read_bytes()
        if validate_backups(first, second) != 'valid' or [sha(first), sha(second)] != previous['backup_sha256']:
            raise ValueError('Prepared backups changed or WBI already invalid; no write')
        current = read_partition(camera, folder, prefix + '-prewrite.bin', ops)
        if current != first:
            raise ValueError('WBI changed since double backup; no write')
        # Exclusive marker prevents retries after ANY possibly completed write.
        ops.save_private(folder, base + '-consumed.json', json.dumps({'attempt': token}).encode())
        remote = '/tmp/jiritsu/zve10-wifi-' + token
        ops.run(camera, 'busybox mkdir -p /tmp/jiritsu')
        ops.run(camera, 'busybox mkdir ' + remote)
        try:
            ops.upload_verified(camera, remote + '/ud_wbi_drop.elf', tool)
            if sha(CONFIG) != CONFIG_HASH:
                raise RuntimeError('Internal WBI configuration hash mismatch; no execution')
            ops.upload_verified(camera, remote + '/partinf.conf', CONFIG)
            # Recheck identity immediately before execution, without trusting USB path alone.
            if identity(camera, ops, folder) != report['identity']:
                raise ValueError('Device identity changed before execution; no write')
            ops.run(camera, 'busybox chmod 700 ' + remote + '/ud_wbi_drop.elf')
            report['write_attempted'] = True
            # A failed command may still have written: always attempt full readback.
            execution_error = None
            try:
                report['sony_output'] = ops.run(camera, 'cd ' + remote + ' && ./ud_wbi_drop.elf partinf.conf')
            except Exception as exc:
                execution_error = exc
                report['execution_error'] = repr(exc)
            after = read_partition(camera, folder, prefix + '-after.bin', ops)
            report['after_sha256'] = sha(after)
            validate_after(first, after)
            if execution_error:
                raise RuntimeError('Sony command failed despite expected readback; review evidence before continuing') from execution_error
            if report['sony_output'].strip() != '[UD_WBI_DROP] /dev/nflasha5 wbi_drop':
                raise RuntimeError('Unexpected Sony output; readback saved, STOP')
            report['status'] = 'invalidated; full readback verified, only first 512 bytes zeroed'
        finally:
            # Fixed filenames only; never recursive removal or automatic partition restore.
            cleanup_errors = []
            for command in ('busybox rm -f ' + remote + '/ud_wbi_drop.elf ' + remote + '/partinf.conf',
                            'busybox rmdir ' + remote):
                try:
                    ops.run(camera, command)
                except Exception as exc:
                    cleanup_errors.append(repr(exc))
            if cleanup_errors:
                report['cleanup_errors'] = cleanup_errors
                # Preserve an in-flight exception, otherwise fail the transaction.
                import sys
                if sys.exc_info()[0] is None:
                    raise RuntimeError('Temporary WBI files could not be cleaned; STOP')
        record()
        return report
    except Exception as exc:
        report['error'] = repr(exc)
        record()
        raise
