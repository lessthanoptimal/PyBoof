package pyboof;

import boofcv.struct.feature.TupleDesc_F64;
import boofcv.struct.image.GrayU8;
import boofcv.struct.image.GrayF32;
import boofcv.struct.image.InterleavedU8;
import boofcv.struct.image.Planar;
import georegression.struct.point.*;
import boofcv.struct.geo.AssociatedPair;
import boofcv.struct.image.ImageDataType;

import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
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
	public void read_List_Point2D(List list, int type_ordinal ) {
	    Type type = Type.values()[type_ordinal];
	    mmf.position(0);
		if( mmf.getShort() != type.ordinal() ) {
			throw new RuntimeException("Memmap not of type "+type);
		}
		int numBytes = type.getDataType().getNumBits()/8;
		int numElements = mmf.getInt();
		byte data[] = new byte[numBytes*2];
		ByteBuffer bb = ByteBuffer.wrap(data);

       switch( type ) {
            case LIST_POINT2D_U16:
            case LIST_POINT2D_S16: {
                    for (int i = 0; i < numElements; i++) {
                        mmf.get(data,0,data.length);
                        Point2D_I16 p = new Point2D_I16();
                        p.x = bb.getShort(0);
                        p.y = bb.getShort(2);
                        list.add( p );
                    }
                } break;

            case LIST_POINT2D_S32: {
                    for (int i = 0; i < numElements; i++) {
                        mmf.get(data,0,data.length);
                        Point2D_I32 p = new Point2D_I32();
                        p.x = bb.getInt(0);
                        p.y = bb.getInt(4);
                        list.add( p );
                    }
                } break;

            case LIST_POINT2D_F32: {
                    for (int i = 0; i < numElements; i++) {
                        mmf.get(data,0,data.length);
                        Point2D_F32 p = new Point2D_F32();
                        p.x = bb.getFloat(0);
                        p.y = bb.getFloat(4);
                        list.add( p );
                    }
                } break;

            case LIST_POINT2D_F64: {
                for (int i = 0; i < numElements; i++) {
                    mmf.get(data,0,data.length);
                    Point2D_F64 p = new Point2D_F64();
                    p.x = bb.getDouble(0);
                    p.y = bb.getDouble(8);
                    list.add( p );
                }
            } break;
        }

	}

    public void write_List_Point2D(List<?> list , int type_ordinal , int startIndex ) {
        Type type = Type.values()[type_ordinal];

        int numBytes = type.getDataType().getNumBits()/8;

        int maxElements = (mmf.limit()-100)/(numBytes*2);
		int numElements = Math.min(list.size(),maxElements);

		mmf.position(0);
		mmf.putShort((short)type.ordinal());
		mmf.putInt(numElements);

        switch( type ) {
            case LIST_POINT2D_U16:
            case LIST_POINT2D_S16: {
                    for (int i = 0; i < numElements; i++) {
                        Point2D_I16 p = (Point2D_I16)list.get(startIndex+i);

                        mmf.putShort(p.x);
                        mmf.putShort(p.y);
                    }
                } break;

            case LIST_POINT2D_S32: {
                    for (int i = 0; i < numElements; i++) {
                        Point2D_I32 p = (Point2D_I32)list.get(startIndex+i);

                        mmf.putInt(p.x);
                        mmf.putInt(p.y);
                    }
                } break;

            case LIST_POINT2D_F32: {
                    for (int i = 0; i < numElements; i++) {
                        Point2D_F32 p = (Point2D_F32)list.get(startIndex+i);

                        mmf.putFloat(p.x);
                        mmf.putFloat(p.y);
                    }
                } break;

            case LIST_POINT2D_F64: {
                for (int i = 0; i < numElements; i++) {
                    Point2D_F64 p = (Point2D_F64)list.get(startIndex+i);

                    mmf.putDouble(p.x);
                    mmf.putDouble(p.y);
                }
            } break;
        }
    }

	public void read_List_AssociatedPair_F64(List<AssociatedPair> list ) {
		mmf.position(0);
		if( mmf.getShort() != Type.LIST_ASSOCIATED_PAIR_F64.ordinal() ) {
			throw new RuntimeException("Not a list of AssociatedPair!");
		}
		int numElements = mmf.getInt();

		byte data[] = new byte[8*4];
		ByteBuffer bb = ByteBuffer.wrap(data);
		for (int i = 0; i < numElements; i++) {
			mmf.get(data,0,data.length);
			AssociatedPair p = new AssociatedPair();
			p.p1.x = bb.getDouble(0);
			p.p1.y = bb.getDouble(8);
			p.p2.x = bb.getDouble(16);
			p.p2.y = bb.getDouble(24);
			list.add( p );
		}
	}

	public void write_List_AssociatedPair_F64(List<AssociatedPair> list , int startIndex ) {

		int maxElements = (mmf.limit()-100)/(8*4);
		int numElements = Math.min(list.size(),maxElements);

		mmf.position(0);
		mmf.putShort((short)Type.LIST_ASSOCIATED_PAIR_F64.ordinal());
		mmf.putInt(numElements);

		for (int i = 0; i < numElements; i++) {
			AssociatedPair p = list.get(startIndex+i);

			mmf.putDouble(p.p1.x);
			mmf.putDouble(p.p1.y);
			mmf.putDouble(p.p2.x);
			mmf.putDouble(p.p2.y);
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

	public void writeImage_PU8_as_IU8( Planar<GrayU8> image ) {
		mmf.position(0);
		mmf.putShort((short)Type.IMAGE_U8.ordinal());
		mmf.putInt(image.getWidth());
		mmf.putInt(image.getHeight());
		mmf.putInt(image.getNumBands());

		int pixelIndex = 0;
		for (int y = 0; y < image.height; y++) {
		    for (int x = 0; x < image.width; x++, pixelIndex++) {
		        for( int band = 0; band < image.bands.length; band++ ) {
		            mmf.put(image.bands[band].data[pixelIndex]);
		        }
		    }
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
		image.data = new float[width*height];
		ByteBuffer.wrap(tmp).order(ByteOrder.LITTLE_ENDIAN).asFloatBuffer().get(image.data);

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
		IMAGE_U8(ImageDataType.U8),
		IMAGE_F32(ImageDataType.F32),
		LIST_POINT2D_U16(ImageDataType.U16),
		LIST_POINT2D_S16(ImageDataType.S16),
		LIST_POINT2D_S32(ImageDataType.S32),
		LIST_POINT2D_F32(ImageDataType.F32),
		LIST_POINT2D_F64(ImageDataType.F64),
		LIST_TUPLE_F32(ImageDataType.F32),
		LIST_TUPLE_F64(ImageDataType.F64),
		LIST_ASSOCIATED_PAIR_F32(ImageDataType.F32),
		LIST_ASSOCIATED_PAIR_F64(ImageDataType.F64);

		ImageDataType dataType;

		Type(ImageDataType dataType) {
		    this.dataType = dataType;
		}

		public ImageDataType getDataType() {
    		return dataType;
		}
	}
}
