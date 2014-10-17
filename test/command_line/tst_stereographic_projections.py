from __future__ import division

def run():
  import os
  import libtbx.load_env
  from libtbx import easy_run
  try:
    dials_regression = libtbx.env.dist_path('dials_regression')
  except KeyError, e:
    print 'FAIL: dials_regression not configured'
    exit(0)

  path = os.path.join(dials_regression, "experiment_test_data")
  cmd = "dials.stereographic_projection '%s/experiment_1.json' hkl_limit=4 plot.show=False" %(path)
  result = easy_run.fully_buffered(cmd).raise_if_errors()
  assert os.path.exists("projections.txt")


if __name__ == '__main__':
  from dials.test import cd_auto
  with cd_auto(__file__):
    run()
    print "OK"
