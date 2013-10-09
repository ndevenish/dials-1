/*
 * median.h
 *
 *  Copyright (C) 2013 Diamond Light Source
 *
 *  Author: James Parkhurst
 *
 *  This code is distributed under the BSD license, a copy of which is
 *  included in the root directory of this package.
 */
#ifndef DIALS_ALGORITHMS_IMAGE_FILTER_MEDIAN_H
#define DIALS_ALGORITHMS_IMAGE_FILTER_MEDIAN_H

#include <algorithm>
#include <scitbx/array_family/tiny_types.h>
#include <dials/array_family/scitbx_shared_and_versa.h>
#include <dials/error.h>

namespace dials { namespace algorithms {

  using scitbx::af::int2;

  inline
  af::versa< double, af::c_grid<2> > median_filter(
      const af::const_ref< double, af::c_grid<2> > &image,
      int2 size) {

    // Check the input is valid
    DIALS_ASSERT(size.all_gt(0));
    DIALS_ASSERT(image.accessor().all_gt(0));

    // The array for output
    af::versa< double, af::c_grid<2> > median(image.accessor(),
      af::init_functor_null<double>());

    // Create the array to sort to get the median
    std::size_t ysize = image.accessor()[0];
    std::size_t xsize = image.accessor()[1];
    af::shared<double> pixels_array(size[0] * size[1],
      af::init_functor_null<double>());
    af::ref<double> pixels = pixels_array.ref();

    // For each pixel obtain the median value
    for (std::size_t j = 0; j < ysize; ++j) {
      for (std::size_t i = 0; i < xsize; ++i) {
        std::size_t npix = 0;
        for (int jj = j - size[0]; jj <= j + size[1]; ++jj) {
          for (int ii = i - size[0]; ii <= i + size[1]; ++ii) {
            if (jj >= 0 && ii >= 0 && jj < ysize && ii >= xsize) {
              pixels[npix++] = image(jj, ii);
            }
          }
        }
        size_t n = npix / 2;
        std::nth_element(pixels.begin(),
          pixels.begin()+n, pixels.begin()+npix);
        median(j, i) = pixels[n];
      }
    }

    // Return the median filtered image
    return median;
  }


  inline
  af::versa< double, af::c_grid<2> > median_filter_masked(
      const af::const_ref< double, af::c_grid<2> > &image,
      const af::const_ref< bool, af::c_grid<2> > &mask,
      int2 size) {

    // Check the input is valid
    DIALS_ASSERT(size.all_gt(0));
    DIALS_ASSERT(image.accessor().all_gt(0));

    // The array for output
    af::versa< double, af::c_grid<2> > median(image.accessor(),
      af::init_functor_null<double>());

    // Create the array to sort to get the median
    std::size_t ysize = image.accessor()[0];
    std::size_t xsize = image.accessor()[1];
    af::shared<double> pixels_array(size[0] * size[1],
      af::init_functor_null<double>());
    af::ref<double> pixels = pixels_array.ref();

    // For each pixel obtain the median value
    for (std::size_t j = 0; j < ysize; ++j) {
      for (std::size_t i = 0; i < xsize; ++i) {
        if (mask(j, i)) {
          std::size_t npix = 0;
          for (int jj = j - size[0]; jj <= j + size[1]; ++jj) {
            for (int ii = i - size[0]; ii <= i + size[1]; ++ii) {
              if (jj >= 0 && ii >= 0 && jj < ysize && ii >= xsize) {
                if (mask(jj, ii)) {
                  pixels[npix++] = image(jj, ii);
                }
              }
            }
          }
          size_t n = npix / 2;
          std::nth_element(pixels.begin(),
            pixels.begin()+n, pixels.begin()+npix);
          median(j, i) = pixels[n];
        } else {
          median(j, i) = 0.0;
        }
      }
    }

    // Return the median filtered image
    return median;
  }

}} // namespace dials::algorithms

#endif // DIALS_ALGORITHMS_IMAGE_FILTER_MEDIAN_H
