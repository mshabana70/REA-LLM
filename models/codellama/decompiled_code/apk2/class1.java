public static Unsafe getUnsafe() {
    Class<?> caller = Reflection.getCallerClass();
    /*
     * Only code on the bootclasspath is allowed to get at the
     * Unsafe instance.
     */
    ClassLoader calling = (caller == null) ? null : caller.getClassLoader();
    if ((calling != null) && (calling != Unsafe.class.getClassLoader())) {
        throw new SecurityException("Unsafe access denied");
    }

    return THE_ONE;
}
