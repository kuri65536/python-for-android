--- host-src/Modules/posixmodule.c	2017-07-08 12:33:27.000000000 +0900
+++ python-src_arm/Modules/posixmodule.c	2017-08-31 16:04:39.609134000 +0900
@@ -416,6 +416,11 @@
 }
 #endif
 
+/* Android doesn't expose AT_EACCESS - manually define it. */
+#if !defined(AT_EACCESS) && defined(__ANDROID__)
+#define AT_EACCESS     0x200
+#endif
+
 
 #ifndef MS_WINDOWS
 PyObject *
@@ -1937,7 +1942,7 @@
     PyStructSequence_SET_ITEM(v, 1,
                               PyLong_FromUnsignedLongLong(st->st_ino));
 #else
-    Py_BUILD_ASSERT(sizeof(unsigned long) >= sizeof(st->st_ino));
+    // Py_BUILD_ASSERT(sizeof(unsigned long) >= sizeof(st->st_ino));
     PyStructSequence_SET_ITEM(v, 1, PyLong_FromUnsignedLong(st->st_ino));
 #endif
 #ifdef MS_WINDOWS
