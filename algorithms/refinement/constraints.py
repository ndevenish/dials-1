#!/usr/bin/env python
#
#  constraints.py
#
#  Copyright (C) 2017 Diamond Light Source and STFC Rutherford Appleton
#                     Laboratory, UK.
#
#  Author: David Waterman
#
#  This code is distributed under the BSD license, a copy of which is
#  included in the root directory of this package.

from __future__ import absolute_import, division
from libtbx.phil import parse
from libtbx.utils import Sorry
from scitbx.array_family import flex
from scitbx import sparse

# PHIL options for constraints
phil_str = '''
constraints
  .help = "Parameter equal shift constraints to use in refinement."
  .expert_level = 2
{
  id = None
    .help = "Index of experiments affected by this constraint to look up which"
            "parameterisations to apply the restraint to. If an identified"
            "parameterisation affects multiple experiments then the index"
            "of any one of those experiments suffices to identify that"
            "parameterisation."
    .type = ints(value_min=0)

  parameters = None
    .type = strings
    .help = "Constrain specified parameters of each parameterisation by a list"
            "of 0-based indices or partial names to match"

  apply_to_all = False
    .help = "Shorthand to constrain the parameterisations across all experiments"
    .type = bool
}

'''

phil_scope = parse(phil_str)

class EqualShiftConstraint(object):
  """A single constraint between parameters of the same type in different
  parameterisations"""

  def __init__(self, indices, parameter_vector):

    self.indices = indices
    self.constrained_value = flex.mean(parameter_vector.select(indices))
    self._shifts = parameter_vector.select(indices) - self.constrained_value

  def set_constrained_value(self, val):
    self.constrained_value = val

  def get_expanded_values(self):
    return self.constrained_value + self._shifts

class ConstraintManager(object):
  def __init__(self, constraints, n_full_params):

    self._constraints = constraints

    # constraints should be a list of EqualShiftConstraint objects
    assert len(self._constraints) > 0

    self._n_full_params = n_full_params
    full_idx = flex.size_t_range(n_full_params)
    self._constrained_idx = flex.size_t([i for c in self._constraints for i in c.indices])
    keep = flex.bool(self._n_full_params, True)
    keep.set_selected(self._constrained_idx, False)
    self._unconstrained_idx = full_idx.select(keep)
    self._n_unconstrained_params = len(self._unconstrained_idx)

  def constrain_parameters(self, x):

    assert len(x) == self._n_full_params

    constrained_vals = flex.double([c.constrained_value for c in self._constraints])

    # select unconstrained parameters only
    unconstrained_x = x.select(self._unconstrained_idx)

    constrained_x = flex.double.concatenate(unconstrained_x, constrained_vals)

    return constrained_x

  def expand_parameters(self, constrained_x):

    unconstrained_part = constrained_x[0:self._n_unconstrained_params]
    constrained_part = constrained_x[self._n_unconstrained_params:]

    # update constrained parameter values
    for v, c in zip(constrained_part, self._constraints):
      c.set_constrained_value(v)

    expanded = flex.double([v for c in self._constraints for v in c.get_expanded_values()])

    full_x = flex.double(self._n_full_params)
    full_x.set_selected(self._unconstrained_idx, unconstrained_part)
    full_x.set_selected(self._constrained_idx, expanded)

    return full_x

