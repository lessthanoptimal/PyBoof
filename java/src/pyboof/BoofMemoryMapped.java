package pyboof;

import boofcv.struct.feature.TupleDesc_F64;
import boofcv.struct.image.GrayU8;
import boofcv.struct.image.GrayF32;
import boofcv.struct.image.InterleavedU8;
import georegression.struct.point.Point2D_F64;

import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.ByteBuffer;
import java.nio.MappedByteBuffer;
import java.nio.channels.FileChannel;
import java.util.List;

/**
 * @author Peter Abeles
 */
public class BoofMemoryMapped {
	MappedByteBuffer mmf;

	public BoofMemoryMapped( String filePath , int sizeMB ) {
		try {
			int size = sizeMB*1024*1024;
			mmf = new RandomAccessFile(filePath, "rw")
					.getChannel().map(FileChannel.MapMode.READ_WRITE, 0, size );
//			System.out.println("Created mmap file "+filePath+" size "+sizeMB+" MB");
//			System.out.println("limit.  Requested "+size+"  found "+mmf.limit());
		} catch (IOException e) {
			throw new RuntimeException(e);
		}
	}

	/**
	 * Reads elements from the memory map file and appends them to the current list
	 * @param list List in which the elements are appended into
	 */
	public void read_List_TupleF64(List<TupleDesc_F64> list ) {
		mmf.position(0);
		if( mmf.getShort() != Type.LIST_TUPLE_F64.ordinal() ) {
			throw new RuntimeException("Not a list of tuples!");
		}
		int numElements = mmf.getInt();
		int dof = mmf.getInt();

		byte data[] = new byte[8*dof];
		ByteBuffer bb = ByteBuffer.wrap(data);
		for (int i = 0; i < numElements; i++) {
			mmf.get(data,0,data.length);
			TupleDesc_F64 desc = new TupleDesc_F64(dof);
			for (int j = 0; j < dof; j++) {
				desc.value[j] = bb.getDouble(j*8);
			}
			list.add( desc );
		}
	}

	public void write_List_TupleF64(List<TupleDesc_F64> list , int startIndex ) {
		int DOF = list.size()>0?list.get(0).size() : 0;

		int maxElements = (mmf.limit()-100)/(8*DOF);
		int numElements = Math.min(list.size(),maxElements);

		mmf.position(0);
		mmf.putShort((short)Type.LIST_TUPLE_F64.ordinal());
		mmf.putInt(numElements);
		mmf.putInt(DOF);

		for (int i = 0; i < numElements; i++) {
			TupleDesc_F64 desc = list.get(startIndex+i);

			for (int j = 0; j < DOF; j++) {
				mmf.putDouble(desc.value[j]);
			}
		}
	}

	/**
	 * Reads elements from the memory map file and appends them to the current list
	 * @param list List in which the elements are appended into
	 */
	public void read_List_Point2DF64(List<Point2D_F64> list ) {
		mmf.position(0);
		if( mmf.getShort() != Type.LIST_POINT2D_F64.ordinal() ) {
			throw new RuntimeException("Not a list of Point2D_F64!");
		}
		int numElements = mmf.getInt();

		byte data[] = new byte[8*2];
		ByteBuffer bb = ByteBuffer.wrap(data);
		for (int i = 0; i < numElements; i++) {
			mmf.get(data,0,data.length);
			Point2D_F64 p = new Point2D_F64();
			p.x = bb.getDouble(0);
			p.y = bb.getDouble(8);
			list.add( p );
		}
	}

	public void write_List_Point2DF64(List<Point2D_F64> list , int startIndex ) {

		int maxElements = (mmf.limit()-100)/(8*2);
		int numElements = Math.min(list.size(),maxElements);

		mmf.position(0);
		mmf.putShort((short)Type.LIST_POINT2D_F64.ordinal());
		mmf.putInt(numElements);

		for (int i = 0; i < numElements; i++) {
			Point2D_F64 p = list.get(startIndex+i);

			mmf.putDouble(p.x);
			mmf.putDouble(p.y);
		}
	}

	public void writeImage_U8(GrayU8 image ) {
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

	public void writeImage_F32(GrayF32 image ) {
		mmf.position(0);
		mmf.putShort((short)Type.IMAGE_F32.ordinal());
		mmf.putInt(image.getWidth());
		mmf.putInt(image.getHeight());
		mmf.putInt(1);

		ByteBuffer buffer = ByteBuffer.allocate(4 * image.width);

		for (int y = 0; y < image.height; y++) {
			int start = y*image.stride + image.startIndex;
			buffer.clear();
			for (int x = 0; x < image.width; x++ ) {
				buffer.putFloat(image.data[start+x]);
			}
			mmf.put(buffer.array(),0,image.width*4);
		}
	}

	public GrayU8 readImage_U8(GrayU8 image ) {
		mmf.position(0);
		if( mmf.getShort() != Type.IMAGE_U8.ordinal() ) {
			throw new RuntimeException("Not an image!");
		}
		int width = mmf.getInt();
		int height = mmf.getInt();
		int numBands = mmf.getInt();
		if( numBands != 1 )
			throw new RuntimeException("Expected single band image not "+numBands);

        if( image == null )
            image = new GrayU8(width,height);
        else
    		image.reshape(width,height);
		mmf.get(image.data,0,width*height);

		return image;
	}

	public GrayF32 readImage_F32(GrayF32 image ) {
		mmf.position(0);
		if( mmf.getShort() != Type.IMAGE_F32.ordinal() ) {
			throw new RuntimeException("Not an image!");
		}
		int width = mmf.getInt();
		int height = mmf.getInt();
		int numBands = mmf.getInt();
		if( numBands != 1 )
			throw new RuntimeException("Expected single band image not "+numBands);

        if( image == null )
            image = new GrayF32(width,height);
        else
    		image.reshape(width,height);

		byte[] tmp = new byte[ width*height*4 ];
		mmf.get(tmp,0,width*height);
		image.data = ByteBuffer.wrap(tmp).asFloatBuffer().array();

		return image;
	}

	public InterleavedU8 readImage_IU8( InterleavedU8 image ) {
		mmf.position(0);
		if( mmf.getShort() != Type.IMAGE_U8.ordinal() ) {
			throw new RuntimeException("Not an image!");
		}
		int width = mmf.getInt();
		int height = mmf.getInt();
		int numBands = mmf.getInt();
		if( image == null )
    		image = new InterleavedU8(width, height, numBands);
        else {
            image.numBands = numBands;
            image.reshape(width,height);
        }
		mmf.get(image.data,0,width*height*numBands);

		return image;
	}

	public enum Type
	{
		IMAGE_U8,
		IMAGE_F32,
		LIST_POINT2D_F64,
		LIST_TUPLE_F64
	}
}
