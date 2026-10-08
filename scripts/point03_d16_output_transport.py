"""Read only the existing scientific ZIP into bounded notebook output blocks."""
import base64
import hashlib
import json
from pathlib import Path

d16_transfer_file = Path('/content/Silice_D16_C1_resultados_20261008.zip')
d16_transfer_size = d16_transfer_file.stat().st_size
d16_transfer_block_size = 65536
assert hashlib.sha256(d16_transfer_file.read_bytes()).hexdigest() == '154c97d008acb69c766cd4e802e932e42317f4b7a42e1b6cf985b0374e83064e'


def d16_emit_block(index):
    assert isinstance(index, int) and 0 <= index < (d16_transfer_size+65535)//65536
    with d16_transfer_file.open('rb') as f:
        f.seek(index*d16_transfer_block_size)
        payload = f.read(d16_transfer_block_size)
    print('D16_BLOCK:'+str(index)+':'+str(len(payload)))
    print(base64.b64encode(payload).decode('ascii'))
    print('D16_END:'+str(index))


print(json.dumps({'bytes': d16_transfer_size, 'block_bytes': d16_transfer_block_size,
                  'blocks': (d16_transfer_size+65535)//65536,
                  'sha256': '154c97d008acb69c766cd4e802e932e42317f4b7a42e1b6cf985b0374e83064e'}))
