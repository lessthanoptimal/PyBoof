import math
import py4j.java_gateway as jg
from pyboof import gateway
import pyboof
import numpy as np


class PointCloudViewer(pyboof.JavaWrapper):
    """
    Sprite based point cloud viewer
    """
    def __init__(self):
        self.set_java_object(gateway.jvm.boofcv.visualize.VisualizeData.createPointCloudViewer())

    def clear(self):
        self.java_obj.clearPoints()

    def add_points(self, cloud, color=None):
        java_cloud = gateway.jvm.java.util.ArrayList()
        pyboof.mmap_list_python_to_Point3D(cloud, java_cloud, np.double)

        if color:
            java_color = pyboof.mmap_array_python_to_java(color, pyboof.MmapType.ARRAY_S32)
            self.java_obj.addCloud(java_cloud, java_color)
        else:
            self.java_obj.addCloud(java_cloud)

    def show_in_window(self, width=400, height=400, title="Cloud"):
        java_component = self.java_obj.getComponent()
        java_dimension = gateway.jvm.java.awt.Dimension(int(width), int(height))
        java_component.setPreferredSize(java_dimension)
        show(java_component, title)
        pass

    def set_step(self, step):
        self.java_obj.setTranslationStep(float(step))

    def set_dot_size(self, size=1):
        self.java_obj.setDotSize(int(size))

    def set_camera_hfov(self, radians):
        self.java_obj.setCameraHFov(float(radians))

    def set_camera_to_world(self):
        pass


def show(boof_image, title="Image"):
    gateway.jvm.boofcv.gui.image.ShowImages.showWindow(boof_image, title)


def show_grid(images, columns=-1, title="Image Grid"):
    if type(images) is not tuple or not list:
        images = (images)

    array = gateway.new_array(gateway.jvm.java.awt.image.BufferedImage, len(images))
    for idx, image in enumerate(images):
        if jg.is_instance_of(gateway, image, gateway.jvm.java.awt.image.BufferedImage):
            array[idx] = image
        else:
            array[idx] = gateway.jvm.boofcv.io.image.ConvertBufferedImage.convertTo(image, None, True)

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
        if jg.is_instance_of(gateway, pair[0], gateway.jvm.java.awt.image.BufferedImage):
            buffered.append(pair[0])
        else:
            buffered.append(gateway.jvm.boofcv.io.image.ConvertBufferedImage.convertTo(pair[0], None, True))
        names.append(pair[1])

    panel = gateway.jvm.boofcv.gui.ListDisplayPanel()
    for i in range(len(names)):
        panel.addImage(buffered[i], names[i])
    gateway.jvm.boofcv.gui.image.ShowImages.showWindow(panel, title)


def colorize_gradient(deriv_x, deriv_y):
    return gateway.jvm.boofcv.gui.image.VisualizeImageData.colorizeGradient(deriv_x, deriv_y, -1, None)


def render_binary(binary, invert=False):
    # BUG in Py4J here. It's calling a private function instead of a public function
    #     BoofCV SNAPSHOT works around this issue
    return gateway.jvm.boofcv.gui.binary.VisualizeBinaryData.renderBinary(binary, invert, None)


def visualize_matches(image_left, image_right, points_src, points_dst, match_indexes,
                      title="Associated Features"):
    if type(points_src) is list:
        points_src = pyboof.p2b_list_point2D(points_src, np.double)

    if type(points_dst) is list:
        points_dst = pyboof.p2b_list_point2D(points_dst, np.double)

    if type(match_indexes) is list:
        raise Exception("Haven't bothered to implement python to java conversion for match_indexes yet")

    # If possible, convert images into a BufferedImage data type
    if jg.is_instance_of(gateway, image_left, gateway.jvm.boofcv.struct.image.ImageBase):
        image_left = gateway.jvm.boofcv.io.image.ConvertBufferedImage.convertTo(image_left, None, True)

    if jg.is_instance_of(gateway, image_right, gateway.jvm.boofcv.struct.image.ImageBase):
        image_right = gateway.jvm.boofcv.io.image.ConvertBufferedImage.convertTo(image_right, None, True)

    panel = gateway.jvm.boofcv.gui.feature.AssociationPanel(20)
    panel.setImages(image_left, image_right)
    panel.setAssociation(points_src, points_dst, match_indexes)
    gateway.jvm.boofcv.gui.image.ShowImages.showWindow(panel, title)


def visualize_lines(image, lines, title="Lines"):
    # If possible, convert images into a BufferedImage data type
    if jg.is_instance_of(gateway, image, gateway.jvm.boofcv.struct.image.ImageBase):
        image = gateway.jvm.boofcv.io.image.ConvertBufferedImage.convertTo(image, None, True)

    d = gateway.jvm.java.awt.Dimension(image.getWidth(), image.getHeight())

    if type(lines) is list:
        if len(lines) > 0 and type(lines[0]) is tuple:  # See if it's a list of line and names
            panel = gateway.jvm.boofcv.gui.ListDisplayPanel()
            for o in lines:
                panel_lines = gateway.jvm.boofcv.gui.feature.ImageLinePanel()
                panel_lines.setImage(image)
                panel_lines.setLines(pyboof.p2b_list_LineParametric(o[1], float))
                panel_lines.setPreferredSize(d)
                panel.addItem(panel_lines, o[0])

            gateway.jvm.boofcv.gui.image.ShowImages.showWindow(panel, title)
            return
        else:
            lines = pyboof.p2b_list_LineParametric(lines, float)

    print("lines {}".format(len(lines)))
    print("foo {}".format(lines[0]))

    panel = gateway.jvm.boofcv.gui.feature.ImageLinePanel()
    panel.setImage(image)
    panel.setLines(lines)
    panel.setPreferredSize(d)
    gateway.jvm.boofcv.gui.image.ShowImages.showWindow(panel, title)
