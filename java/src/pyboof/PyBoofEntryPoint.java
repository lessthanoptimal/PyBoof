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

import boofcv.struct.Configuration;

import py4j.GatewayServer;

import boofcv.abst.feature.detdesc.DetectDescribePoint;
import boofcv.struct.feature.TupleDesc;

import georegression.struct.point.Point2D_F64;

import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.List;



/**
 * Must launch this application to use PyBoof
 *
 *
 * @author Peter abeles
 */
public class PyBoofEntryPoint {

	public static void nothing(){}

	public static void main(String[] args) {
		GatewayServer gatewayServer = new GatewayServer(new PyBoofEntryPoint());
		gatewayServer.start();
		System.out.println("Gateway Server Started");
	}

	public static List<TupleDesc> extractFeatures( DetectDescribePoint alg ) {
		int N = alg.getNumberOfFeatures();

		List<TupleDesc> array = new ArrayList<TupleDesc>();
		for (int i = 0; i < N; i++) {
			array.add(alg.getDescription(i).copy());
		}

		return array;
	}

	public static List<Point2D_F64> extractPoints( DetectDescribePoint alg ) {
		int N = alg.getNumberOfFeatures();

		List<Point2D_F64> array = new ArrayList<Point2D_F64>();
		for (int i = 0; i < N; i++) {
			array.add(alg.getLocation(i).copy());
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
