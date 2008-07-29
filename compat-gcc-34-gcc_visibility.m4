AC_DEFUN([HIDE_INLINES], [
    visibility_inlines_hidden=yes
    if test "X$CXX" != "X"; then
	AC_MSG_CHECKING([whether ${CXX} accepts -fvisbility-inlines-hidden])
	visbility_old_cxxflags="$CXXFLAGS"
	CXXFLAGS="$CXXFLAGS -fvisibility-inlines-hidden"
	AC_TRY_COMPILE(, , , visibility_inlines_hidden=no)
	echo $visibility_inlines_hidden
	if test "X$visibility_inlines_hidden" = "Xno"; then
	    CXXFLAGS="$visibility_old_cxxflags"
	fi
    fi
])

AC_DEFUN([HIDDEN_ATTRIBUTE], [
    if test "X$CC" != "X"; then
	AC_MSG_CHECKING([GCC visibility attribute])
	AC_TRY_COMPILE(
	    [int __attribute__((visibility("hidden"))) test();],
	    [],
	    AC_DEFINE(HAVE_HIDDEN_ATTRIBUTE, 1, [])
	    AC_MSG_RESULT(yes),
	    AC_MSG_RESULT(no)
	)
    fi
])
