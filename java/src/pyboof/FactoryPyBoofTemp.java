package pyboof;

import boofcv.abst.sfm.d2.ImageMotion2D;
import boofcv.abst.sfm.d2.PlToGrayMotion2D;
import boofcv.abst.tracker.PointTracker;
import boofcv.alg.sfm.d2.StitchingFromMotion2D;
import boofcv.factory.sfm.FactoryMotion2D;
import boofcv.factory.tracker.ConfigPointTracker;
import boofcv.factory.tracker.FactoryPointTracker;
import boofcv.struct.image.*;
import georegression.struct.homography.Homography2D_F64;

/**
 * Simplifying factories for when BoofCV doesn't have a good simple factory
 *
 * @author Peter Abeles
 */
public class FactoryPyBoofTemp {
    public static <T extends ImageGray<T>> StitchingFromMotion2D<Planar<T>, Homography2D_F64>
    basicVideoMosaic(ConfigPointTracker configTracker, Class<T> grayType ) {

        PointTracker<T> tracker = FactoryPointTracker.tracker(configTracker,grayType, null);

        // This estimates the 2D image motion
        // An Affine2D_F64 model also works quite well.
        ImageMotion2D<T, Homography2D_F64> motion2D = FactoryMotion2D.createMotion2D(
                200, 3, 2, 100, 0.6, 0.5, false, tracker, new Homography2D_F64());

        // wrap it so it output color images while estimating motion from gray
        ImageMotion2D<Planar<T>, Homography2D_F64> motion2DColor = new PlToGrayMotion2D<>(motion2D, grayType);

        // This fuses the images together
       return FactoryMotion2D.createVideoStitch(0.5, motion2DColor, ImageType.pl(3, grayType));
    }
}
