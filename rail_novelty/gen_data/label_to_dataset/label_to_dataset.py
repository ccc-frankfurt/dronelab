import math
from pathlib import Path
import subprocess
import shutil


dir = "/projects/sysl2/rail_novelity_training/gen_data/handpicked_rails"
out = "/projects/sysl2/rail_novelity_training/gen_data/masks"
#for path in Path(dir).resolve().rglob('*.json'):
#    stem = path.stem
#    out_path = path.with_name(stem+"_mask")
#    subprocess.run(["labelme_json_to_dataset", str(path), "-o", str(out_path)])


Path(out).mkdir(parents=True, exist_ok=True)
for path in Path(dir).resolve().rglob('label.png'):
    out_img = Path(out)/(path.parent.stem+".png")
    shutil.copyfile(path, out_img)
    print(out_img)
    #subprocess.run(["labelme_json_to_dataset", str(path), "-o", str(out_path)])
