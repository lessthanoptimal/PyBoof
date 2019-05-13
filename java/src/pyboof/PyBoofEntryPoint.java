/*
 * Copyright (c) 2011-2015, Peter Abeles. All Rights Reserved.
 *
 * This file is part of BoofCV (http://boofcv.org).
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package pyboof;


import boofcv.abst.feature.detdesc.DetectDescribePoint;
import boofcv.factory.filter.binary.ConfigThreshold;
import boofcv.factory.filter.binary.ThresholdType;
import boofcv.struct.Configuration;
import boofcv.struct.feature.TupleDesc;
import georegression.struct.point.Point2D_F64;
import org.ddogleg.struct.FastQueue;
import py4j.GatewayServer;
import boofcv.concurrency.BoofConcurrency;

import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.List;


// TODO visualize features.  location, scale, orienation
// TODO visualize matches. image, image, location, location, index pairs

/**
 * Must launch this application to use PyBoof
 *
 *
 * @author Peter abeles
 */
public class PyBoofEntryPoint {

	public static BoofMemoryMapped mmap;
	public static String buildDate;

	/**
	 * Called in python to see if the JVM is set up correctly
	 */
	public static void nothing(){}

	public static void main(String[] args) {
		GatewayServer gatewayServer = new GatewayServer(new PyBoofEntryPoint());
		gatewayServer.start();
		System.out.println("Gateway Server Started");
	}

	public static void setMaxThreads( int maxThreads ) {
		BoofConcurrency.USE_CONCURRENT = maxThreads > 1;
		if( BoofConcurrency.USE_CONCURRENT ) {
			BoofConcurrency.setMaxThreads(maxThreads);
		}
	}

	public static String getBuildDate() {
		return buildDate;
	}

	public static void setBuildDate(String buildDate) {
		PyBoofEntryPoint.buildDate = buildDate;
	}

	public static void initializeMmap(String filePath , int sizeMB ) {
		// no need to do special cleanup if mmap already exists.  It will be cleaned up by GC
		mmap = new BoofMemoryMapped(filePath,sizeMB);
	}

	/**
	 * Hack around 'global' being a keyword in Python
	 */
	public static ConfigThreshold createGlobalThreshold( ThresholdType type ) {
		return ConfigThreshold.global(type);
	}

	public static FastQueue listToFastQueue( List list , Class type , boolean declare ) {
		FastQueue ret = new FastQueue(list.size(),type,declare);

		for (int i = 0; i < list.size(); i++) {
			ret.add(list.get(i));
		}

		return ret;
	}

	public static List<TupleDesc> extractFeatures( DetectDescribePoint alg , boolean copy ) {
		int N = alg.getNumberOfFeatures();

		List<TupleDesc> array = new ArrayList<TupleDesc>();
		for (int i = 0; i < N; i++) {
			if( copy)
				array.add(alg.getDescription(i).copy());
			else
				array.add(alg.getDescription(i));
		}

		return array;
	}

	public static List<Point2D_F64> extractPoints( DetectDescribePoint alg , boolean copy ) {
		int N = alg.getNumberOfFeatures();

		List<Point2D_F64> array = new ArrayList<Point2D_F64>();
		for (int i = 0; i < N; i++) {
			if( copy )
				array.add(alg.getLocation(i).copy());
			else
				array.add(alg.getLocation(i));
		}

		return array;
	}

	public static List<String> getPublicFields( String classPath ) {
		List<String> list = new ArrayList<String>();

		try {
			Field[] fields = Class.forName(classPath).getFields();
			for( Field f : fields ) {
				list.add(f.getName());
			}
		} catch (ClassNotFoundException e) {
			System.err.println("Can't find class "+classPath);
			System.exit(1);
		}

		return list;
	}

	public static List<String> getPublicFields( Class typeClass ) {
		List<String> list = new ArrayList<String>();

		Field[] fields = typeClass.getFields();
		for( Field f : fields ) {
			list.add(f.getName());
		}

		return list;
	}

	public static boolean isConfigClass( Object o ) {
		return o instanceof Configuration;
	}

	public static boolean isClass( Class c , String path ) {

		try {
			//System.out.println("Class = "+c+"  forname = "+Class.forName(path));
			Class found = Class.forName(path);
			return c.isAssignableFrom(found) || found.isAssignableFrom(c);
		} catch (ClassNotFoundException e) {
			return false;
		}
	}
}
