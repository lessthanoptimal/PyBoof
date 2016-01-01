package pyboof;

import boofcv.struct.feature.BrightFeature;
import boofcv.struct.feature.TupleDesc_F64;
import georegression.struct.point.Point2D_F64;

import java.io.BufferedOutputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.List;

/**
 * @author Peter Abeles
 */
public class FileIO {

	public static void saveList( List list , Class type , String filePath ) throws IOException {
		if( type == TupleDesc_F64.class ) {
			saveRawTupleDescF64(list, filePath);
		} else if( type == BrightFeature.class ) {
			saveRawTupleDescF64(list,filePath);
		} else if( type == Point2D_F64.class ){
			saveRawPoint2DF64(list, filePath);
		} else {
			throw new RuntimeException("Unknown data type "+type.getSimpleName());
		}
	}

	public static void saveRawTupleDescF64( List<TupleDesc_F64> list , String filePath ) throws IOException {
		OutputStream out = new BufferedOutputStream(new FileOutputStream(filePath));

		String type = "list\n"+TupleDesc_F64.class.getCanonicalName()+"\n";
		out.write(type.getBytes());
		writeInt(list.size(), out);


		for (int i = 0; i < list.size(); i++) {
			TupleDesc_F64 t = list.get(i);
			writeInt(t.size(), out);

			for (int j = 0; j < t.size(); j++) {
				writeLong(Double.doubleToRawLongBits(t.value[j]), out);
			}
		}

		out.close();
	}

	public static void saveRawPoint2DF64( List<Point2D_F64> list , String filePath ) throws IOException {
		OutputStream out = new FileOutputStream(filePath);

		String type = "list\n"+Point2D_F64.class.getCanonicalName()+"\n";
		out.write(type.getBytes());
		writeInt(list.size(), out);

		for (int i = 0; i < list.size(); i++) {
			Point2D_F64 t = list.get(i);
			writeLong(Double.doubleToRawLongBits(t.x), out);
			writeLong(Double.doubleToRawLongBits(t.y), out);
		}

		out.close();
	}

	public static void writeInt( int value , OutputStream out ) throws IOException {
		out.write(value>>24);
		out.write(value>>16);
		out.write(value >> 8);
		out.write(value);
	}

	public static void writeLong( long value , OutputStream out ) throws IOException {
		int upper = (int)(value>>32);
		int lower = (int)value;

		out.write(upper>>24);
		out.write(upper>>16);
		out.write(upper>>8);
		out.write(upper);
		out.write(lower>>24);
		out.write(lower>>16);
		out.write(lower>>8);
		out.write(lower);
	}
}
