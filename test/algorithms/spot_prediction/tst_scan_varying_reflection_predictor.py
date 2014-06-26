from __future__ import division

class Test(object):

  def __init__(self):
    import libtbx.load_env
    try:
      dials_regression = libtbx.env.dist_path('dials_regression')
    except KeyError, e:
      print 'FAIL: dials_regression not configured'
      return

    import os
    from dials.util.command_line import Importer
    path = os.path.join(
      dials_regression,
      'prediction_test_data',
      'experiments_scan_varying_crystal.json')

    importer = Importer([path])
    assert(importer.experiments is not None)
    self.experiments = importer.experiments
    assert(len(self.experiments) == 1)
    assert(self.experiments[0].crystal.num_scan_points ==
           self.experiments[0].scan.get_num_images() + 1)

  def run(self):
    self.tst_vs_old()
    #self.tst_with_hkl()
    #self.tst_with_hkl_and_panel()
    #self.tst_with_hkl_and_panel_list()

  def predict_old(self):
    from dials.algorithms.refinement.prediction.predictors import \
      ScanVaryingReflectionListGenerator
    dmin = self.experiments[0].detector.get_max_resolution(
      self.experiments[0].beam.get_s0())
    predict = ScanVaryingReflectionListGenerator(
      self.experiments[0].crystal,
      self.experiments[0].beam,
      self.experiments[0].goniometer,
      self.experiments[0].scan,
      dmin)
    from time import time
    st = time()
    result = predict()
    #print "Old Time: ", time() - st
    from dials.model.data import ReflectionList
    from dials.array_family import flex
    result = ReflectionList(result).to_table()

    s1 = result['s1']
    xyz = result['xyzcal.mm']
    ind = flex.size_t()
    for i in range(len(result)):
      try:
        coord = self.experiments[0].detector.get_ray_intersection(s1[i])
        xyz[i] = coord[1] + (xyz[i][2],)
      except Exception:
        ind.append(i)
    result.del_selected(ind)
    return result

  def predict_new(self, hkl=None, frame=None, panel=None):
    from dials.algorithms.spot_prediction import ScanVaryingReflectionPredictor
    from time import time
    from dials.array_family import flex
    st = time()
    predict = ScanVaryingReflectionPredictor(self.experiments[0])
    #if hkl is None:
    A = [self.experiments[0].crystal.get_A_at_scan_point(i) for i in
           range(self.experiments[0].crystal.num_scan_points)]
    result = predict.for_ub(flex.mat3_double(A))
    #else:
      #if panel is None:
        #result = predict(hkl, frame)
      #else:
        #result = predict(hkl, frame, panel)

    #print "New Time: ", time() - st
    return result

  def tst_vs_old(self):
    r_old = self.predict_old()
    r_new = self.predict_new()
    assert(len(r_old) == len(r_new))
    eps = 1e-7
    for r1, r2 in zip(r_old.rows(), r_new.rows()):
      assert(r1['miller_index'] == r2['miller_index'])
      assert(r1['panel'] == r2['panel'])
      assert(r1['entering'] == r2['entering'])
      assert(all(abs(a-b) < eps for a, b in zip(r1['s1'], r2['s1'])))
      assert(all(abs(a-b) < eps for a, b in zip(r1['xyzcal.mm'], r2['xyzcal.mm'])))
    print 'OK'

  #def tst_with_hkl(self):
    #from dials.algorithms.spot_prediction import ReekeIndexGenerator
    #from dials.array_family import flex
    #from scitbx import matrix
    #import scitbx

    #m2 = self.experiments[0].goniometer.get_rotation_axis()
    #s0 = self.experiments[0].beam.get_s0()
    #dmin = self.experiments[0].detector.get_max_resolution(s0)
    #margin = 1
    #scan = self.experiments[0].scan
    #crystal = self.experiments[0].crystal
    #frame_0 = scan.get_array_range()[0]
    #step = 1

    #all_indices = flex.miller_index()
    #all_frames = flex.int()
    #for frame in range(*scan.get_array_range()):

      #phi_beg = scan.get_angle_from_array_index(frame, deg = False)
      #phi_end = scan.get_angle_from_array_index(frame + step, deg = False)
      #r_beg = matrix.sqr(scitbx.math.r3_rotation_axis_and_angle_as_matrix(
          #axis = m2, angle = phi_beg, deg = False))
      #r_end = matrix.sqr(scitbx.math.r3_rotation_axis_and_angle_as_matrix(
          #axis = m2, angle = phi_end, deg = False))

      #A1 = r_beg * crystal.get_A_at_scan_point(frame - frame_0)

      #A2 = r_end * crystal.get_A_at_scan_point(frame - frame_0 + step)

      #indices = ReekeIndexGenerator(A1, A2, m2, s0, dmin, margin)
      #indices = indices.to_array()
      #all_indices.extend(indices)
      #all_frames.extend(flex.int(len(indices), frame))

    #r_old = self.predict_new()
    #r_new = self.predict_new(all_indices, all_frames)
    #assert(len(r_old) == len(r_new))
    #print 'OK'

  #def tst_with_hkl_and_panel(self):
    #from dials.algorithms.spot_prediction import ReekeIndexGenerator
    #from dials.array_family import flex
    #from scitbx import matrix
    #import scitbx

    #m2 = self.experiments[0].goniometer.get_rotation_axis()
    #s0 = self.experiments[0].beam.get_s0()
    #dmin = self.experiments[0].detector.get_max_resolution(s0)
    #margin = 1
    #scan = self.experiments[0].scan
    #crystal = self.experiments[0].crystal
    #frame_0 = scan.get_array_range()[0]
    #step = 1

    #all_indices = flex.miller_index()
    #all_frames = flex.int()
    #for frame in range(*scan.get_array_range()):

      #phi_beg = scan.get_angle_from_array_index(frame, deg = False)
      #phi_end = scan.get_angle_from_array_index(frame + step, deg = False)
      #r_beg = matrix.sqr(scitbx.math.r3_rotation_axis_and_angle_as_matrix(
          #axis = m2, angle = phi_beg, deg = False))
      #r_end = matrix.sqr(scitbx.math.r3_rotation_axis_and_angle_as_matrix(
          #axis = m2, angle = phi_end, deg = False))

      #A1 = r_beg * crystal.get_A_at_scan_point(frame - frame_0)

      #A2 = r_end * crystal.get_A_at_scan_point(frame - frame_0 + step)

      #indices = ReekeIndexGenerator(A1, A2, m2, s0, dmin, margin)
      #indices = indices.to_array()
      #all_indices.extend(indices)
      #all_frames.extend(flex.int(len(indices), frame))

    #r_old = self.predict_new()
    #try:
      #r_new = self.predict_new(all_indices, all_frames, 1)
      #assert(False)
    #except Exception:
      #pass

    #r_new = self.predict_new(all_indices, all_frames, 0)
    #assert(len(r_old) < len(r_new))
    #print 'OK'

  #def tst_with_hkl_and_panel_list(self):

    #from dials.algorithms.spot_prediction import ReekeIndexGenerator
    #from dials.array_family import flex
    #from scitbx import matrix
    #import scitbx

    #m2 = self.experiments[0].goniometer.get_rotation_axis()
    #s0 = self.experiments[0].beam.get_s0()
    #dmin = self.experiments[0].detector.get_max_resolution(s0)
    #margin = 1
    #scan = self.experiments[0].scan
    #crystal = self.experiments[0].crystal
    #frame_0 = scan.get_array_range()[0]
    #step = 1

    #all_indices = flex.miller_index()
    #all_frames = flex.int()
    #for frame in range(*scan.get_array_range()):

      #phi_beg = scan.get_angle_from_array_index(frame, deg = False)
      #phi_end = scan.get_angle_from_array_index(frame + step, deg = False)
      #r_beg = matrix.sqr(scitbx.math.r3_rotation_axis_and_angle_as_matrix(
          #axis = m2, angle = phi_beg, deg = False))
      #r_end = matrix.sqr(scitbx.math.r3_rotation_axis_and_angle_as_matrix(
          #axis = m2, angle = phi_end, deg = False))

      #A1 = r_beg * crystal.get_A_at_scan_point(frame - frame_0)

      #A2 = r_end * crystal.get_A_at_scan_point(frame - frame_0 + step)

      #indices = ReekeIndexGenerator(A1, A2, m2, s0, dmin, margin)
      #indices = indices.to_array()
      #all_indices.extend(indices)
      #all_frames.extend(flex.int(len(indices), frame))

    #r_old = self.predict_new()
    #try:
      #r_new = self.predict_new(all_indices, all_frames,
                               #flex.size_t(len(all_indices), 1))
      #assert(False)
    #except Exception:
      #pass

    #r_new = self.predict_new(all_indices, all_frames,
                             #flex.size_t(len(all_indices), 0))
    #assert(len(r_old) < len(r_new))
    #print 'OK'

if __name__ == '__main__':

  from dials.test import cd_auto
  with cd_auto(__file__):
    test = Test()
    test.run()
