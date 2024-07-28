import itk
import vtk

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

def segmentation_tumeur(input_filepath, output_filepath, seed, lower, upper, mode=1):
    input_image = input_filepath

    smoother = itk.GradientAnisotropicDiffusionImageFilter.New(
        Input=input_image, NumberOfIterations=20, TimeStep=0.04, ConductanceParameter=3)
    smoother.Update()

    connected_threshold = itk.ConnectedThresholdImageFilter.New(smoother.GetOutput())
    connected_threshold.SetReplaceValue(255)
    connected_threshold.SetLower(lower)
    connected_threshold.SetUpper(upper)

    new_seed = (seed[0], seed[1], seed[2])
    connected_threshold.SetSeed(new_seed)
    connected_threshold.Update()
    in_type = itk.output(connected_threshold)
    dimension = input_image.GetImageDimension()
    output_type = itk.Image[itk.UC, dimension]
    rescaler = itk.RescaleIntensityImageFilter[in_type, output_type].New(connected_threshold)
    rescaler_image = rescaler.GetOutput()

    # POUR RECUPERER LA PARTIE EXTERIEURE (donc sans la tumeur)
    structuring_element = itk.FlatStructuringElement[input_image.GetImageDimension()].Ball(9)
    morph_filter = itk.BinaryMorphologicalOpeningImageFilter.New(Input=rescaler, Kernel=structuring_element)
    morph_filter.Update()

    subtract_filter = itk.SubtractImageFilter.New(Input1=rescaler_image, Input2=morph_filter.GetOutput())
    subtract_filter.Update()
    abs_filter = itk.AbsImageFilter.New(Input=subtract_filter.GetOutput())
    abs_filter.Update()

    abs_filter2 = None

    # POUR RECUPERER L'IMAGE AVEC LA TUMEUR (union entre la partie extérieure et l'image de base)
    if mode == 1:
        union_filter = itk.MaximumImageFilter.New(Input1=rescaler_image, Input2=abs_filter.GetOutput())
        union_filter.Update()
        abs_filter2 = itk.AbsImageFilter.New(Input=union_filter.GetOutput())
        abs_filter2.Update()
        
    
    # POUR RECUPERER LA ZONE DE LA TUMEUR
    if mode == 2:
        structuring_element = itk.FlatStructuringElement[abs_filter.GetOutput().GetImageDimension()].Ball(1)
        morpho1 = itk.BinaryErodeImageFilter.New(Input=abs_filter, Kernel=structuring_element)
        structuring_element = itk.FlatStructuringElement[abs_filter.GetOutput().GetImageDimension()].Ball(20)
        morpho2 = itk.BinaryDilateImageFilter.New(Input=morpho1, Kernel=structuring_element)
        union_filter = itk.MaximumImageFilter.New(Input1=rescaler_image, Input2=morpho2.GetOutput())
        union_filter.Update()
        abs_filter2 = itk.AbsImageFilter.New(Input=union_filter.GetOutput())
        abs_filter2.Update()
        
    # (inversion)
    res_image = abs_filter2.GetOutput()
    stats = itk.StatisticsImageFilter.New(Input=res_image)
    stats.Update()
    min_intensity = stats.GetMinimum()
    max_intensity = stats.GetMaximum()
    invert_filter = itk.ShiftScaleImageFilter.New(Input=res_image)
    invert_filter.SetShift(-max_intensity)
    invert_filter.SetScale(-1.0)
    invert_filter.Update()
    output_image = invert_filter.GetOutput()
    
    itk.imwrite(output_image, output_filepath)

def image_difference(image1, image2):
    if not itk.template(image1)[1] == itk.template(image2)[1]:
        raise ValueError("Les images d'entrée doivent avoir le même type et les mêmes dimensions.")

    subtract_filter = itk.SubtractImageFilter.New(Input1=image1, Input2=image2)
    subtract_filter.Update()

    abs_filter = itk.AbsImageFilter.New(Input=subtract_filter.GetOutput())
    abs_filter.Update()

    return abs_filter.GetOutput()

def read_image(filepath):
    image = itk.imread(filepath, itk.UC)
    vtk_image = itk.vtk_image_from_image(image)
    return vtk_image

def setup_contour(vtk_image, value):
    contour = vtk.vtkContourFilter()
    contour.SetInputData(vtk_image)
    contour.SetValue(0, value)

    contour_mapper = vtk.vtkPolyDataMapper()
    contour_mapper.SetInputConnection(contour.GetOutputPort())
    contour_mapper.ScalarVisibilityOff()

    contour_actor = vtk.vtkActor()
    contour_actor.SetMapper(contour_mapper)

    return contour_actor

def setup_volume(vtk_image, color, opacity):
    opacity_fun = vtk.vtkPiecewiseFunction()
    opacity_fun.AddPoint(0, 0.0)
    opacity_fun.AddPoint(255, opacity)

    color_fun = vtk.vtkColorTransferFunction()
    color_fun.AddRGBPoint(0.0, color[0], color[1], color[2])
    color_fun.AddRGBPoint(255.0, color[0], color[1], color[2])

    volume_property = vtk.vtkVolumeProperty()
    volume_property.SetScalarOpacity(opacity_fun)
    volume_property.SetColor(color_fun)
    volume_property.SetInterpolationTypeToLinear()

    volume_mapper = vtk.vtkSmartVolumeMapper()
    volume_mapper.SetInputData(vtk_image)

    volume = vtk.vtkVolume()
    volume.SetProperty(volume_property)
    volume.SetMapper(volume_mapper)

    return volume

def create_text_actor(text):
    text_actor = vtk.vtkTextActor()
    text_actor.SetInput(text)
    text_actor.GetTextProperty().SetFontSize(24)
    text_actor.GetTextProperty().SetColor(1, 1, 1)
    text_actor.SetPosition(10, 10)
    return text_actor

def render_scene(actors_list, volumes_list, titles):
    render_window = vtk.vtkRenderWindow()

    renderers = [vtk.vtkRenderer() for _ in range(3)]
    
    for i, renderer in enumerate(renderers):
        renderer.SetViewport(i / 3.0, 0.0, (i + 1) / 3.0, 1.0)
        render_window.AddRenderer(renderer)
        renderer.SetBackground(0.1, 0.1, 0.1)
        
        # Add actors and volumes to each renderer
        for actor in actors_list[i]:
            renderer.AddActor(actor)
        for volume in volumes_list[i]:
            renderer.AddVolume(volume)
        
        # Add title to the renderer
        text_actor = create_text_actor(titles[i])
        renderer.AddActor2D(text_actor)

    render_window.SetSize(1800, 600)

    interactors = [vtk.vtkRenderWindowInteractor() for _ in range(3)]
    for interactor in interactors:
        interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        interactor.SetRenderWindow(render_window)

    for interactor, renderer in zip(interactors, renderers):
        interactor.AddObserver("RenderEvent", lambda obj, event: renderer.GetRenderWindow().Render())

    render_window.Render()

    for interactor in interactors:
        interactor.Start()

if __name__ == "__main__":
    # PARTIE ITK
    print("Recalage de l'image")
    PixelType = itk.F
    moving= itk.imread("Data/case6_gre2.nrrd",PixelType)
    fixed = itk.imread("Data/case6_gre1.nrrd",PixelType)
    moved = recalage_data(fixed,moving)
    seed = (43, 123, 122)
    
    print("Premiere segmentation de tumeur")
    segmentation_tumeur(fixed, "case6_gre1_segmented.nrrd", seed, 0, 350, mode=1)
    segmentation_tumeur(fixed, "tumor_zone1.nrrd", seed, 0, 350, mode=2)
    print("Deuxieme segmentation de tumeur")
    segmentation_tumeur(moved, "case6_gre2_segmented.nrrd", seed, 0, 350, mode=1)
    segmentation_tumeur(moved, "tumor_zone2.nrrd", seed, 0, 350, mode=2)
    print("Creation de l'image différence")
    image1 = itk.imread("case6_gre1_segmented.nrrd", itk.F)
    image2 = itk.imread("case6_gre2_segmented.nrrd", itk.F)
    image_diff = image_difference(image1, image2)
    itk.imwrite(image_diff, "image_diff.nrrd")
    

    # PARTIE VTK
    print("Affichage des résultats")
    vtk_image1 = read_image('case6_gre1_segmented.nrrd')
    vtk_image2 = read_image('tumor_zone1.nrrd')
    vtk_image3 = read_image('case6_gre2_segmented.nrrd')
    vtk_image4 = read_image('tumor_zone2.nrrd')
    vtk_image5 = read_image('image_diff.nrrd')

    # Set up volumes with different properties
    volume1 = setup_volume(vtk_image1, color=(0.8, 0.4, 0.2), opacity=0.01)
    volume2 = setup_volume(vtk_image2, color=(1.0, 0.0, 0.0), opacity=1.0)
    volume3 = setup_volume(vtk_image3, color=(0.8, 0.4, 0.2), opacity=0.01)
    volume4 = setup_volume(vtk_image4, color=(0.0, 0.0, 1.0), opacity=1.0)
    volume5 = setup_volume(vtk_image5, color=(0.8, 0.4, 0.2), opacity=0.05)

    volumes_list = [[volume1, volume2], [volume3, volume4], [volume5]]
    actors_list = [[], [], []]
    titles = ["Image Tumeur 1", "Image Tumeur 2", "Différence"]

    render_scene(actors_list, volumes_list, titles)
