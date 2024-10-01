import logging
import os
import tarfile
import uuid

from .base import basedriver
from ..utils import filemgr, tar_safe_extract, extract_and_copy


class tardriver(basedriver):
    def __init__(self, ctx, model):
        super().__init__(ctx, model)

    def cleanup(self):
        os.unlink(os.path.join(self.ctx.path, self.model.params['location']))

    def update(self, mgr):
        path = mgr.acquire(self.model.params['location'])
        mgr.release(path)
        self.ctx.state.update(dependencies={
            self.model.name: self.model.state(location=os.path.relpath(path, self.ctx.path), driver='tar')
        })

    def unpack(self, mgr, locations):
        with filemgr(self.ctx, uuid.uuid4().hex, True) as tmp:
            with tarfile.open(os.path.join(self.ctx.path, self.model.params['location'])) as tar:
                logging.info(" Unpacking archive...")
                def is_within_directory(directory, target):
                    
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                
                    prefix = os.path.commonprefix([abs_directory, abs_target])
                    
                    return prefix == abs_directory
                
                def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                
                    for member in tar.getmembers():
                        member_path = os.path.join(path, member.name)
                        if not is_within_directory(path, member_path):
                            raise Exception("Attempted Path Traversal in Tar File")
                
                    tar.extractall(path, members, numeric_owner=numeric_owner) 
                    
                
                safe_extract(tar, tmp._path)
            for l in locations:
                if l['source'][0] == '/':
                    l['source'] = l['source'][1:]
                if l['dest'][0] == '/':
                    l['dest'] = l['dest'][1:]
                logging.info(" Extracting {} to {}".format(l['source'], l['dest']))
                src = os.path.join(tmp._path, l['source'])
                dst = os.path.join(mgr._path, l['dest'])
                if os.path.isdir(src):
                    ensure_path_exists(dst)
                else:
                    ensure_path_exists(os.path.dirname(dst))
                shutil.copytree(src, dst, dirs_exist_ok=True)
            self._ctx._state.update(build={
                self._model.name: self._model.state(driver='tar')
            })