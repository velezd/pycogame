from PIL import Image
import os
import sys
 
def crop_img(img_path):
    img = Image.open(img_path)
    img_dir = os.path.dirname(img_path)
    img_name, img_ext = os.path.splitext(os.path.basename(img_path))
    new_dir = os.path.join(img_dir, 'cropped')
    if not os.path.exists(new_dir):
        os.mkdir(new_dir)

    width, height = img.size
 
    for x in range(1, width):
        img_cropped = img.crop((0, 0, width-x, height))
        img_cropped.save(os.path.join(new_dir, img_name + '_r' + str(x) + img_ext))
        img_cropped = img.crop((x, 0, width, height))
        img_cropped.save(os.path.join(new_dir, img_name + '_l' + str(x) + img_ext))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Provide path to image')
        sys.exit(1)

    crop_img(sys.argv[1])