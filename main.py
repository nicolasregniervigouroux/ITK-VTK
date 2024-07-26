import itk
import vtk
import matplotlib
import matplotlib.pyplot as plt

def recalage_data(fixed,moving):
    dimension = fixed.GetImageDimension()
    FixedImageType = type(fixed)
    MovingImageType = type(moving)
    #initialisation du transform initiale
    TransformType = itk.TranslationTransform[itk.D,dimension]
    initial_transform = TransformType.New()

    #initialisation de l'optimizer
    optimizer = itk.RegularStepGradientDescentOptimizerv4.New()
    optimizer.SetLearningRate(4.0)
    optimizer.SetMinimumStepLength(0.001)
    optimizer.SetNumberOfIterations(30)

    #initialisation de la metrique
    metric = itk.MeanSquaresImageToImageMetricv4[FixedImageType, MovingImageType].New()
    fixed_interpolation = itk.LinearInterpolateImageFunction[FixedImageType, itk.D].New()
    metric.SetFixedInterpolator(fixed_interpolation)

    #initialisation de la registration
    registration = itk.ImageRegistrationMethodv4[FixedImageType, MovingImageType].New()
    registration.SetMetric(metric)
    registration.SetOptimizer(optimizer)
    registration.SetFixedImage(fixed)
    registration.SetMovingImage(moving)
    registration.SetInitialTransform(initial_transform)

    registration.SetNumberOfLevels(1)

    #lancement du calcul du recalage
    registration.Update()

    transform = registration.GetTransform()
    
    resampler = itk.ResampleImageFilter.New(Input=moving, Transform=transform, UseReferenceImage=True,
                                            ReferenceImage=fixed)
    resampler.SetDefaultPixelValue(100)
    resampler.Update()
    resampling1 = resampler.GetOutput()

    return resampling1
def segmentation_tumeur(image,seed,lower,upper):

    #Ajout d'un filtre gaussien pour lisser les bords
    smoothing = itk.SmoothingRecursiveGaussianImageFilter.New(Input=image, Sigma=1.5)
    smoothing.Update()
    smoother = smoothing.GetOutput()

    # Initialisation d'un RegionGrowing
    connected_threshold = itk.ConnectedThresholdImageFilter.New(smoother)
    connected_threshold.SetReplaceValue(255)
    connected_threshold.SetLower(lower)
    connected_threshold.SetUpper(upper)

    connected_threshold.SetSeed(seed)
    connected_threshold.Update()

    return connected_threshold.GetOutput()

if __name__ == "__main__":
    PixelType = itk.F
    moving= itk.imread("Data/case6_gre2.nrrd",PixelType)
    fixed = itk.imread("Data/case6_gre1.nrrd",PixelType)
    moved = recalage_data(fixed,moving)
    seed1 = (100, 50, 60)
    seed2 = (110, 70, 60)
    tumor1=segmentation_tumeur(fixed,seed1,60,130)
    tumor2=segmentation_tumeur(moved,seed2,60,130)