package pyboof;

import boofcv.struct.image.ImageUInt8;
import boofcv.struct.image.InterleavedU8;

import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.MappedByteBuffer;
import java.nio.channels.FileChannel;

/**
 * @author Peter Abeles
 */
public class BoofMemoryMapped {
	MappedByteBuffer mmf;

	public BoofMemoryMapped( String filePath , int sizeMB ) {
		try {
			mmf = new RandomAccessFile(filePath, "rw")
					.getChannel().map(FileChannel.MapMode.READ_WRITE, 0, sizeMB*1024*1024 );
//			System.out.println("Created mmap file "+filePath+" size "+sizeMB+" MB");
		} catch (IOException e) {
			throw new RuntimeException(e);
		}
	}

	public void writeImage_SU8(ImageUInt8 image ) {
		mmf.position(0);
		mmf.putShort((short)Type.IMAGE_U8.ordinal());
		mmf.putInt(image.getWidth());
		mmf.putInt(image.getHeight());
		mmf.putInt(1);
		for (int y = 0; y < image.height; y++) {
			int start = y*image.stride + image.startIndex;
			mmf.put(image.data,start,image.width);
		}
	}

	public void readImage_SU8(ImageUInt8 image ) {
		mmf.position(0);
		if( mmf.getShort() != Type.IMAGE_U8.ordinal() ) {
			throw new RuntimeException("Not an image!");
		}
		int width = mmf.getInt();
		int height = mmf.getInt();
		int numBands = mmf.getInt();
		if( numBands != 1 )
			throw new RuntimeException("Expected single band image not "+numBands);

		image.reshape(width,height);
		mmf.get(image.data,0,width*height);
	}

	public void readImage_IU8(InterleavedU8 image ) {
		mmf.position(0);
		if( mmf.getShort() != Type.IMAGE_U8.ordinal() ) {
			throw new RuntimeException("Not an image!");
		}
		int width = mmf.getInt();
		int height = mmf.getInt();
		image.numBands = mmf.getInt();

		image.reshape(width,height);
		mmf.get(image.data,0,width*height*image.numBands);
	}

	public enum Type
	{
		IMAGE_U8,
		POINTS_F64,
	}
}
