
#include <boost/python.hpp>
#include <boost/python/def.hpp>
#include "../beam.h"

using namespace boost::python;
using namespace dials::equipment;

namespace dials { namespace equipment { namespace boost_python {

void export_beam()
{
    class_<beam>("beam")
        .def(init <scitbx::vec3 <double> > ((
            arg("direction"))))
        .def(init <scitbx::vec3 <double>, double> ((
            arg("direction"), 
            arg("wavelength"))))
        .add_property("direction",  
            &beam::get_direction)
        .add_property("wavelength", 
            &beam::get_wavelength);
}

}}}
