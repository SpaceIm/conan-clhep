import glob
import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

class ClhepConan(ConanFile):
    name = "clhep"
    description = "Class Library for High Energy Physics."
    license = "LGPL-3.0-only"
    topics = ("conan", "clhep", "cern", "hep", "high energy", "physics", "geometry", "algebra")
    homepage = "http://proj-clhep.web.cern.ch/proj-clhep"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    short_paths = True
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            raise ConanInvalidConfiguration("CLHEP doesn't properly build its shared libs with Visual Studio")
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            raise ConanInvalidConfiguration("CLHEP doesn't support MinGW")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.version, self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CLHEP_SINGLE_THREAD"] = False
        self._cmake.definitions["CLHEP_BUILD_DOCS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy(pattern="COPYING*", dst="licenses", src=os.path.join(self._source_subfolder, "CLHEP"))
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "bin"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "CLHEP-{}".format(self.version)))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        patterns_to_delete = ["*CLHEP.*", "*CLHEPS.*", "*CLHEP-{}.*".format(self.version), "*CLHEPS-{}.*".format(self.version)] # combined lib (duplicate of components libs)
        patterns_to_delete.extend(["*.a"] if self.options.shared else ["*.so", "*.dylib"])
        for pattern_to_delete in patterns_to_delete:
            for lib_file in glob.glob(os.path.join(self.package_folder, "lib", pattern_to_delete)):
                os.remove(lib_file)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "CLHEP"
        self.cpp_info.names["cmake_find_package_multi"] = "CLHEP"
        self.cpp_info.names["pkg_config"] = "clhep"
        # Vector
        vector_name = "Vector" if self.options.shared else "VectorS"
        self.cpp_info.components["vector"].names["cmake_find_package"] = vector_name
        self.cpp_info.components["vector"].names["cmake_find_package_multi"] = vector_name
        self.cpp_info.components["vector"].names["pkg_config"] = "clhep-vector"
        self.cpp_info.components["vector"].libs = ["CLHEP-{0}-{1}".format(vector_name, self.version)]
        if self.settings.os == "Linux":
            self.cpp_info.components["vector"].system_libs = ["m", "pthread"]
        # Evaluator
        evaluator_name = "Evaluator" if self.options.shared else "EvaluatorS"
        self.cpp_info.components["evaluator"].names["cmake_find_package"] = evaluator_name
        self.cpp_info.components["evaluator"].names["cmake_find_package_multi"] = evaluator_name
        self.cpp_info.components["evaluator"].names["pkg_config"] = "clhep-evaluator"
        self.cpp_info.components["evaluator"].libs = ["CLHEP-{0}-{1}".format(evaluator_name, self.version)]
        if self.settings.os == "Linux":
            self.cpp_info.components["evaluator"].system_libs = ["m", "pthread"]
        # GenericFunctions
        genericfunctions_name = "GenericFunctions" if self.options.shared else "GenericFunctionsS"
        self.cpp_info.components["genericfunctions"].names["cmake_find_package"] = genericfunctions_name
        self.cpp_info.components["genericfunctions"].names["cmake_find_package_multi"] = genericfunctions_name
        self.cpp_info.components["genericfunctions"].names["pkg_config"] = "clhep-genericfunctions"
        self.cpp_info.components["genericfunctions"].libs = ["CLHEP-{0}-{1}".format(genericfunctions_name, self.version)]
        if self.settings.os == "Linux":
            self.cpp_info.components["genericfunctions"].system_libs = ["m", "pthread"]
        # Geometry
        geometry_name = "Geometry" if self.options.shared else "GeometryS"
        self.cpp_info.components["geometry"].names["cmake_find_package"] = geometry_name
        self.cpp_info.components["geometry"].names["cmake_find_package_multi"] = geometry_name
        self.cpp_info.components["geometry"].names["pkg_config"] = "clhep-geometry"
        self.cpp_info.components["geometry"].libs = ["CLHEP-{0}-{1}".format(geometry_name, self.version)]
        if self.settings.os == "Linux":
            self.cpp_info.components["geometry"].system_libs = ["m", "pthread"]
        self.cpp_info.components["geometry"].requires = ["vector"]
        # Random
        random_name = "Random" if self.options.shared else "RandomS"
        self.cpp_info.components["random"].names["cmake_find_package"] = random_name
        self.cpp_info.components["random"].names["cmake_find_package_multi"] = random_name
        self.cpp_info.components["random"].names["pkg_config"] = "clhep-random"
        self.cpp_info.components["random"].libs = ["CLHEP-{0}-{1}".format(random_name, self.version)]
        if self.settings.os == "Linux":
            self.cpp_info.components["random"].system_libs = ["m", "pthread"]
        # Matrix
        matrix_name = "Matrix" if self.options.shared else "MatrixS"
        self.cpp_info.components["matrix"].names["cmake_find_package"] = matrix_name
        self.cpp_info.components["matrix"].names["cmake_find_package_multi"] = matrix_name
        self.cpp_info.components["matrix"].names["pkg_config"] = "clhep-matrix"
        self.cpp_info.components["matrix"].libs = ["CLHEP-{0}-{1}".format(matrix_name, self.version)]
        if self.settings.os == "Linux":
            self.cpp_info.components["matrix"].system_libs = ["m", "pthread"]
        self.cpp_info.components["matrix"].requires = ["random", "vector"]
        # RandomObjects
        randomobjects_name = "RandomObjects" if self.options.shared else "RandomObjectsS"
        self.cpp_info.components["randomobjects"].names["cmake_find_package"] = randomobjects_name
        self.cpp_info.components["randomobjects"].names["cmake_find_package_multi"] = randomobjects_name
        self.cpp_info.components["randomobjects"].names["pkg_config"] = "clhep-randomobjects"
        self.cpp_info.components["randomobjects"].libs = ["CLHEP-{0}-{1}".format(randomobjects_name, self.version)]
        if self.settings.os == "Linux":
            self.cpp_info.components["randomobjects"].system_libs = ["m"]
        self.cpp_info.components["randomobjects"].requires = ["random", "matrix", "vector"]
        # Cast
        cast_name = "Cast" if self.options.shared else "CastS"
        self.cpp_info.components["cast"].names["cmake_find_package"] = cast_name
        self.cpp_info.components["cast"].names["cmake_find_package_multi"] = cast_name
        self.cpp_info.components["cast"].names["pkg_config"] = "clhep-cast"
        self.cpp_info.components["cast"].libs = ["CLHEP-{0}-{1}".format(cast_name, self.version)]
        if self.settings.os == "Linux":
            self.cpp_info.components["cast"].system_libs = ["pthread"]
        # RefCount
        refcount_name = "RefCount" if self.options.shared else "RefCountS"
        self.cpp_info.components["refcount"].names["cmake_find_package"] = refcount_name
        self.cpp_info.components["refcount"].names["cmake_find_package_multi"] = refcount_name
        self.cpp_info.components["refcount"].names["pkg_config"] = "clhep-refcount"
        self.cpp_info.components["refcount"].libs = ["CLHEP-{0}-{1}".format(refcount_name, self.version)]
        if self.settings.os == "Linux":
            self.cpp_info.components["refcount"].system_libs = ["pthread"]
        # Exceptions
        exceptions_name = "Exceptions" if self.options.shared else "ExceptionsS"
        self.cpp_info.components["exceptions"].names["cmake_find_package"] = exceptions_name
        self.cpp_info.components["exceptions"].names["cmake_find_package_multi"] = exceptions_name
        self.cpp_info.components["exceptions"].names["pkg_config"] = "clhep-exceptions"
        self.cpp_info.components["exceptions"].libs = ["CLHEP-{0}-{1}".format(exceptions_name, self.version)]
        self.cpp_info.components["exceptions"].requires = ["cast", "refcount"]
        # CLHEP (global imported target including all CLHEP components)
        global_cmake = "CLHEP" if self.options.shared else "CLHEPS"
        self.cpp_info.components["clheplib"].names["cmake_find_package"] = global_cmake
        self.cpp_info.components["clheplib"].names["cmake_find_package_multi"] = global_cmake
        self.cpp_info.components["clheplib"].requires = [
            "vector", "evaluator", "genericfunctions", "geometry", "random",
            "matrix", "randomobjects", "cast", "refcount", "exceptions"
        ]
