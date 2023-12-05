import folder_paths
from comfy.cli_args import args

from html2image import Html2Image
from PIL import Image
from PIL.PngImagePlugin import PngInfo

import numpy as np
import json
import os
import shutil
import random
import time


class ImageMask(object):
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""
        self.current_directory = os.path.dirname(os.path.realpath(__file__))
        self.frontdir = f"{self.current_directory}/"

    def merge_imgs(self, background, mask, createimage):
        frontimage = Image.open(self.frontdir + mask + ".png")
        background = Image.open(background)
        frontimage = frontimage.convert("RGBA")
        background = background.convert("RGBA")
        background.paste(frontimage, (0, 0), frontimage)
        background.save(createimage)
        print("合并图片成功！")

    @classmethod
    def INPUT_TYPES(s):
        masks = ["无限恐怖768x1024"]
        return {
            "required":
                {"images": ("IMAGE",),
                 "filename_prefix": ("STRING", {"default": "ComfyUI"}),
                 "fps": ("FLOAT", {"default": 6.0, "min": 0.01, "max": 1000.0, "step": 0.01}),
                 "compress_level": ("INT", {"default": 4, "min": 0, "max": 9}),
                 "mask": (masks,),
                 },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ()

    FUNCTION = "image_mask"

    OUTPUT_NODE = True

    CATEGORY = "ComfyUI_Mexx"

    def image_mask(self,
                   images,
                   fps,
                   compress_level,
                   filename_prefix="ComfyUI",
                   mask="无限恐怖768x1024",
                   prompt=None,
                   extra_pnginfo=None):
        filename_prefix += self.prefix_append
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
            filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0])
        results = list()
        pil_images = []
        for image in images:
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            pil_images.append(img)

        metadata = None
        if not args.disable_metadata:
            metadata = PngInfo()
            if prompt is not None:
                metadata.add(b"comf",
                             "prompt".encode("latin-1", "strict") + b"\0" + json.dumps(prompt).encode("latin-1",
                                                                                                      "strict"),
                             after_idat=True)
            if extra_pnginfo is not None:
                for x in extra_pnginfo:
                    metadata.add(b"comf",
                                 x.encode("latin-1", "strict") + b"\0" + json.dumps(extra_pnginfo[x]).encode("latin-1",
                                                                                                             "strict"),
                                 after_idat=True)

        file = f"{filename}_{counter:05}_.png"
        os_path_join_file = os.path.join(full_output_folder, file)
        pil_images[0].save(os_path_join_file, pnginfo=metadata, compress_level=compress_level,
                           save_all=True, duration=int(1000.0 / fps), append_images=pil_images[1:])
        print(f'[Mexx]生成图片地址:{file}')
        createimagefile = f'{mask}_{int(time.time())}.png'
        createimage = f'{self.output_dir}/{createimagefile}'
        self.merge_imgs(os_path_join_file, mask, createimage)
        print(f'[Mexx]生成海报图片:{createimage}')
        results.append({
            "filename": createimagefile,
            "subfolder": subfolder,
            "type": self.type
        })
        return {"ui": {"images": results, "animated": (False,)}}


NODE_CLASS_MAPPINGS = {
    "ComfyUI_Mexx_Image_Mask": ImageMask
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ComfyUI_Mexx_Image_Mask": "ComfyUI_Mexx_Image_Mask"
}
