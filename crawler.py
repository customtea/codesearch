from pathlib import Path

class Crawler():
    def __init__(self, target: str, ext="py") -> None:
        targetpath = Path(target)
        self.files = targetpath.glob(f"**/*.{ext}")
        self.skip_abs_list:list[Path] = []
        self.skip_name_list:list[str] = []
    
    def set_ignore_abspath(self, pathlist: list[str]):
        for tpath in pathlist:
            self.skip_abs_list.append(Path(tpath.strip()).resolve())
    
    def loadfile_ignore_abspath(self, filename):
        with open(filename) as f:
            self.set_ignore_abspath(f.readlines())
    
    def set_ignore_name(self, namelist: list[str]):
        for line in namelist:
            self.skip_name_list.append(line.strip())

    def loadfile_ignore_name(self, filename):
        with open(filename) as f:
            self.set_ignore_name(f.readlines())
    
    def search(self):
        for file in self.files:
            fullpath = file.resolve()
            isskip = False
            for p in fullpath.parents:
                if p in self.skip_abs_list:
                    isskip = True
                    break
                for d in self.skip_name_list:
                    if d in p.stem:
                        isskip = True
                        break
            if isskip:
                isskip = False
            else:
                yield fullpath