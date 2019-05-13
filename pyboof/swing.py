import math
import py4j.java_gateway as jg
from pyboof import gateway
import pyboof
import numpy as np

def show( boof_image , title="Image"):
    gateway.jvm.boofcv.gui.image.ShowImages.showWindow(boof_image,title)

def show_grid( images , columns=-1, title="Image Grid"):
    if type(images) is not tuple or not list:
        images = (images)

    array = gateway.new_array(gateway.jvm.java.awt.image.BufferedImage,len(images))
    for idx,image in enumerate(images):
        if jg.is_instance_of(gateway, image, gateway.jvm.java.awt.image.BufferedImage ):
            array[idx] = image
        else:
            array[idx] = gateway.jvm.boofcv.io.image.ConvertBufferedImage.convertTo(image,None,True)

    # If no grid is specified try to make it square
    if columns <= 0:
        columns = int(math.sqrt(len(images)))
    gateway.jvm.boofcv.gui.image.ShowImages.showGrid(columns, title, array)


def show_list(image_name_pairs, title="Image List"):
    if type(image_name_pairs) is not tuple or not list:
        image_name_pairs = (image_name_pairs)

    names = []
    buffered = []
    for pair in image_name_pairs:
        if jg.is_instance_of(gateway, pair[0], gateway.jvm.java.awt.image.BufferedImage ):
            buffered.append(pair[0])
        else:
            buffered.append( gateway.jvm.boofcv.io.image.ConvertBufferedImage.convertTo(pair[0],None,True) )
        names.append(pair[1])

    panel = gateway.jvm.boofcv.gui.ListDisplayPanel()
    for i in range(len(names)):
        panel.addImage(buffered[i],names[i])
    gateway.jvm.boofcv.gui.image.ShowImages.showWindow(panel, title)


def colorize_gradient( derivX , derivY ):
    return gateway.jvm.boofcv.gui.image.VisualizeImageData.colorizeGradient(derivX,derivY,-1,None)


def render_binary( binary , invert=False):
    return gateway.jvm.boofcv.gui.binary.VisualizeBinaryData.renderBinary(binary,invert,None)


def visualize_matches(image_left , image_right , points_src , points_dst , match_indexes,
                      title = "Associated Features"):

    if type(points_src) is list:
        points_src = pyboof.p2b_list_point2D(points_src,np.double)

    if type(points_dst) is list:
        points_dst = pyboof.p2b_list_point2D(points_dst,np.double)

    if type(match_indexes) is list:
        raise Exception("Haven't bothered to implement python to java conversion for match_indexes yet")

    # If possible, convert images into a BufferedImage data type
    if jg.is_instance_of(gateway, image_left, gateway.jvm.boofcv.struct.image.ImageBase):
        image_left = gateway.jvm.boofcv.io.image.ConvertBufferedImage.convertTo(image_left, None, True)

    if jg.is_instance_of(gateway, image_right, gateway.jvm.boofcv.struct.image.ImageBase):
        image_right = gateway.jvm.boofcv.io.image.ConvertBufferedImage.convertTo(image_right, None, True)

    panel = gateway.jvm.boofcv.gui.feature.AssociationPanel(20)
    panel.setImages( image_left, image_right)
    panel.setAssociation(points_src, points_dst, match_indexes)
    gateway.jvm.boofcv.gui.image.ShowImages.showWindow(panel, title)


