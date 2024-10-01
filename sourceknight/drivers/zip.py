import logging
import os
import platform
import uuid
import zipfile

from .base import basedriver
from ..utils import filemgr, extract_and_copy

class zipdriver(basedriver):
    def __init__(self, ctx, model):
        super().__init__(ctx, model)

    def cleanup(self):
        os.unlink(os.path.join(self.ctx.path, self.model.params['location']))

    def update(self, mgr):
        path = mgr.acquire(self.model.params['location'])
        mgr.release(path)
        self.ctx.state.update(dependencies={
            self.model.name: self.model.state(location=os.path.relpath(path, self.ctx.path), driver='zip')
        })

    def unpack(self, mgr, locations):
        with filemgr(self.ctx, uuid.uuid4().hex, True) as tmp:
            zip_path = os.path.join(self.ctx.path, str(self.model.params['location']))
            tmp_path = tmp.path

            if platform.system() == 'Windows':
                tmp_path = tmp_path.replace('/', '\\')

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                logging.info("Unpacking archive...")

                for member in zip_ref.namelist():
                    member_path = os.path.join(tmp_path, member)
                    abs_tmp_path = os.path.abspath(tmp_path)
                    abs_member_path = os.path.abspath(member_path)

                    if not abs_member_path.startswith(abs_tmp_path):
                        raise Exception("Attempted Path Traversal in Zip File")

                zip_ref.extractall(tmp_path)

            extract_and_copy(self, locations, mgr, tmp)
