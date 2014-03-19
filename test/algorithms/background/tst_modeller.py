from __future__ import division

class Test(object):

  def __init__(self):
    pass

  def run(self):
    self.tst_constant2d_modeller()
    self.tst_constant3d_modeller()
    self.tst_linear2d_modeller()
    self.tst_linear3d_modeller()

  def tst_constant2d_modeller(self):
    from dials.algorithms.background import Constant2dModeller
    modeller = Constant2dModeller()
    eps = 1e-7
    for i in range(10):
      c, data, mask = self.generate_constant_background_2d((9,9,9), 0, 100)
      model = modeller.create(data, mask)
      assert(len(model.params()) == 9)
      for j in range(9):
        assert(abs(model.params()[j] - c[j]) < eps)
    print 'OK'

  def tst_constant3d_modeller(self):
    from dials.algorithms.background import Constant3dModeller
    modeller = Constant3dModeller()
    eps = 1e-7
    for i in range(10):
      c, data, mask = self.generate_constant_background_3d((9,9,9), 0, 100)
      model = modeller.create(data, mask)
      assert(len(model.params()) == 1)
      for j in range(1):
        assert(abs(model.params()[j] - c) < eps)
    print 'OK'

  def tst_linear2d_modeller(self):
    from dials.algorithms.background import Linear2dModeller
    modeller = Linear2dModeller()
    eps = 1e-7
    for i in range(10):
      p, data, mask = self.generate_linear_background_2d((9,9,9), 0, 100)
      model = modeller.create(data, mask)
      assert(len(model.params()) == 3 * 9)
      for j in range(9):
        for k in range(3):
          assert(abs(model.params()[k+j*3] - p[j][k]) < eps)
    print 'OK'

  def tst_linear3d_modeller(self):
    from dials.algorithms.background import Linear3dModeller
    modeller = Linear3dModeller()
    eps = 1e-7
    for i in range(10):
      p, data, mask = self.generate_linear_background_3d((9,9,9), 0, 100)
      model = modeller.create(data, mask)
      assert(len(model.params()) == 4)
      for j in range(4):
        assert(abs(model.params()[j] - p[j]) < eps)
    print 'OK'

  def generate_constant_background_2d(self, size, bmin, bmax):
    from random import uniform
    from scitbx.array_family import flex
    data = flex.double(flex.grid(size), 0)
    mask = flex.bool(flex.grid(size), True)
    slice_size = (1, size[1], size[2])
    cs = []
    for k in range(size[0]):
      c = uniform(bmin, bmax)
      data[k:k+1,:,:] = flex.double(flex.grid(slice_size), c)
      cs.append(c)
    return cs, data, mask

  def generate_constant_background_3d(self, size, bmin, bmax):
    from random import uniform
    from scitbx.array_family import flex
    c = uniform(bmin, bmax)
    data = flex.double(flex.grid(size), c)
    mask = flex.bool(flex.grid(size), True)
    return c, data, mask

  def generate_linear_background_2d(self, size, bmin, bmax):
    from random import uniform
    from scitbx.array_family import flex
    from scitbx import matrix
    slice_size = (1, size[1], size[2])
    data = flex.double(flex.grid(size), 0)
    mask = flex.bool(flex.grid(size), True)
    params = []
    for k in range(size[0]):
      a00 = uniform(bmin, bmax)
      a01 = uniform(bmin, bmax)
      a10 = uniform(bmin, bmax)
      p00 = matrix.col((0.5, 0.5, a00))
      p01 = matrix.col((8.5, 0.5, a01))
      p10 = matrix.col((0.5, 8.5, a10))
      n = (p01 - p00).cross(p10 - p00)
      b = n[0]
      c = n[1]
      d = n[2]
      a = -(b*0.5 + c*0.5 + d*a00)
      a /= -d
      b /= -d
      c /= -d
      for j in range(size[1]):
        for i in range(size[2]):
          data[k,j,i] = a + b * (i + 0.5) + c * (j + 0.5)
      eps = 1e-7
      assert(abs(data[k,0,0] - a00) < eps)
      assert(abs(data[k,8,0] - a10) < eps)
      assert(abs(data[k,0,8] - a01) < eps)
      params.append((a, b, c))
    return params, data, mask

  def generate_linear_background_3d(self, size, bmin, bmax):
    from random import uniform
    from scitbx.array_family import flex
    from scitbx import matrix
    slice_size = (1, size[1], size[2])
    data = flex.double(flex.grid(size), 0)
    mask = flex.bool(flex.grid(size), True)
    a000 = uniform(bmin, bmax)
    a001 = uniform(bmin, bmax)
    a010 = uniform(bmin, bmax)
    a100 = uniform(bmin, bmax)
    p000 = matrix.col((0.5, 0.5, 0.5, a000))
    p001 = matrix.col((8.5, 0.5, 0.5, a001))
    p010 = matrix.col((0.5, 8.5, 0.5, a010))
    p100 = matrix.col((0.5, 0.5, 8.5, a100))
    v1 = p001 - p000
    v2 = p010 - p000
    v3 = p100 - p000
    m1 = matrix.sqr((
      v1[1], v1[2], v1[3],
      v2[1], v2[2], v2[3],
      v3[1], v3[2], v3[3]))
    m2 = matrix.sqr((
      v1[0], v1[2], v1[3],
      v2[0], v2[2], v2[3],
      v3[0], v3[2], v3[3]))
    m3 = matrix.sqr((
      v1[0], v1[1], v1[3],
      v2[0], v2[1], v2[3],
      v3[0], v3[1], v3[3]))
    m4 = matrix.sqr((
      v1[0], v1[1], v1[2],
      v2[0], v2[1], v2[2],
      v3[0], v3[1], v3[2]))
    n = matrix.col((
      m1.determinant(),
      -m2.determinant(),
      m3.determinant(),
      -m4.determinant()))
    b = n[0]
    c = n[1]
    d = n[2]
    e = n[3]
    a = -(b*0.5 + c*0.5 + d*0.5 + e*a000)
    a /= -e
    b /= -e
    c /= -e
    d /= -e
    for k in range(size[0]):
      for j in range(size[1]):
        for i in range(size[2]):
          data[k,j,i] = a + b * (i + 0.5) + c * (j + 0.5) + d * (k + 0.5)
    eps = 1e-7
    assert(abs(data[0,0,0] - a000) < eps)
    assert(abs(data[8,0,0] - a100) < eps)
    assert(abs(data[0,8,0] - a010) < eps)
    assert(abs(data[0,0,8] - a001) < eps)
    return (a, b, c, d), data, mask

if __name__ == '__main__':
  test = Test()
  test.run()
