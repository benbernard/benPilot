// Compile-check adapter for Ubuntu Mesa only. Never deploy this on AGNOS.
// Resolve the real extension procedures; never fake success or hardware output.
#include <cstdlib>
#include <EGL/egl.h>
#include <EGL/eglext.h>

extern "C" EGLImageKHR eglCreateImageKHR(EGLDisplay display, EGLContext context,
                                         EGLenum target, EGLClientBuffer buffer,
                                         const EGLint *attributes) {
  auto function = reinterpret_cast<PFNEGLCREATEIMAGEKHRPROC>(eglGetProcAddress("eglCreateImageKHR"));
  if (!function) std::abort();
  return function(display, context, target, buffer, attributes);
}

extern "C" EGLBoolean eglDestroyImageKHR(EGLDisplay display, EGLImageKHR image) {
  auto function = reinterpret_cast<PFNEGLDESTROYIMAGEKHRPROC>(eglGetProcAddress("eglDestroyImageKHR"));
  if (!function) std::abort();
  return function(display, image);
}
