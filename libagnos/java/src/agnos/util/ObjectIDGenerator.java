//////////////////////////////////////////////////////////////////////////////
// Part of the Agnos RPC Framework
//    http://agnos.sourceforge.net
//
// Copyright 2011, International Business Machines Corp.
//                 Author: Tomer Filiba (tomerf@il.ibm.com)
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//////////////////////////////////////////////////////////////////////////////

package agnos.util;

import java.util.WeakHashMap;


public final class ObjectIDGenerator {
	protected WeakHashMap<Object, Long> map;
	protected Long counter;

	public ObjectIDGenerator() {
		map = new WeakHashMap<Object, Long>();
		counter = new Long(0);
	}

	public synchronized Long getID(Object obj) {
		Object id = map.get(obj);
		if (id != null) {
			return (Long) id;
		} else {
			counter += 1;
			map.put(obj, counter);
			return counter;
		}
	}
}

