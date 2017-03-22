import numpy 
import pandas
from  matplotlib import pyplot
import seaborn


numpy.random.seed(0)
N = 37
_genders= ['Female', 'Male', 'Non-binary', 'No Response']
df = pandas.DataFrame({
    'Height (cm)': numpy.random.uniform(low=130, high=200, size=N),
    'Weight (kg)': numpy.random.uniform(low=30, high=100, size=N),
    'Gender': numpy.random.choice(_genders, size=N)
})

fg = seaborn.FacetGrid(data=df, hue='Gender', hue_order=_genders, aspect=1.61)
fg.map(pyplot.scatter, 'Weight (kg)', 'Height (cm)').add_legend()