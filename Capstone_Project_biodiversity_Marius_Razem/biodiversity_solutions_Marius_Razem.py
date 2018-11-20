# This is Python script was created via JetBrains PyCharm 2018 for the
# Codecademy final Project "Biodiversity", including data analysis
# for the Capstone Option 2: Biodiversity for the National Parks

# All steps were imported according to the Jupiter Notebook
# file provided on Codecademy.com


####  STEP 1: Importing Modules + File inspection ####
# Importing all necessary Python modules
# import codecademylib -->  NOT defined on my PC! (therefore commented)
from matplotlib import pyplot as plt
import pandas as pd
from scipy.stats import chi2_contingency

# Loading DataFrame for the animal data
species = pd.read_csv("species_info.csv")

# Inspection of data structure:
# index | category | scientific_name |
# common_names | conservation_status
# print(species.head())
species.to_csv("results/species_structure.csv", sep = "\t")

####  STEP 2: Gather further Details on the DataFrame ####
# Number of distinct animals in scientific_name
species_count = species.scientific_name.nunique()
print("\n Number of distinct animals: {}".format(species_count))

# Number of animal categories within the national park
species_type = species.category.unique()
print("\n Distinguished animal categories:\n {}".format(species_type))

# Possible values for the conservation_status
conservation_statuses = species.conservation_status.unique()
print("\n (Possible) status values for the conservation:\n {}".format(conservation_statuses))


#### STEP 3: Analyze Species Conservation Status / Data Aggregates ####
# Analysis on the animal conservation statuses
# Create grouping by conservation_status with respect to
# the scientific names of all animals
conservation_counts = species.groupby("conservation_status")["scientific_name"].nunique().reset_index()
print("\n Overview of animal conservation status (not including NaN values):")
print(conservation_counts)


#### STEP 4: Analyze Species Conservation Status II (fixing undocumented NaN values) ####
# Correction of the specimen count with DataFrame.fillna()
species.conservation_status.fillna("No Intervention", inplace = True)
conservation_counts_fixed = species.groupby("conservation_status")["scientific_name"].nunique().reset_index()
print("\n Overview of animal conservation status (fixed):")
print(conservation_counts_fixed)
conservation_counts_fixed.rename(columns = {"scientific_name": "count"})

#### STEP 5: Plot conversation status information ####
# Create new analysis DataFrame with sorted values (sorting by scientific name),
# based on previous conservation count DataFrame
protection_counts = conservation_counts_fixed.sort_values(by = "scientific_name")
protection_counts.to_csv("results/conversations_grouped.csv", sep = "\t")

# Print group information
print("\nAnalysis Data (printing):")
print(protection_counts)

# Create plots with information about
#  - the animal amount (percentages, not given on Codeacademy.com)
#  - the conservation status of all animals (as given on Codecademy.com)
#  - a more detailed view on the conservation status of all animals EXCEPT "No Intervention"

# create figure for the total animal amounts (including analysis DataFrame)
animal_data = species.groupby("category")["scientific_name"].count().reset_index()
animal_data["percent"] = 100 * animal_data.scientific_name / animal_data.scientific_name.sum()
animal_data.rename(columns = {"scientific_name": "amount"}, inplace = True)
print("\nInformation about animal data:")
print(animal_data)
protection_counts.to_csv("results/amount_of_animals.csv", sep = "\t")
animal_data.to_csv("results/animal_overview.csv", sep = "\t")

# Create pie chart for animal data
plt.figure(figsize=(10,7.5))
ax_animals = plt.subplot()
plt.pie(animal_data.amount,
        labels=animal_data.category,
        autopct='%3.2f%%',
        pctdistance=1.1,
        labeldistance=1.2,
        textprops={'fontsize': 10}
)
plt.axis("equal")
plt.savefig("results/animal_distribution.png")

# Create bar chart for conservation information (all data)
plt.figure(figsize=(10,7.5))
ax = plt.subplot()
plt.bar(
  range(0,len(protection_counts)),
  protection_counts.scientific_name
)
plt.ylabel("Number of Species", fontsize = 14)
plt.title("Conservation Status by Species", fontsize = 14)
ax.set_xticks(range(0,len(protection_counts)))
ax.set_xticklabels(protection_counts.conservation_status)
ax.tick_params(axis='both', which='major', labelsize=10)
plt.savefig("results/conversation_all.png")

# Create bar chart for conservation information (without "No Intervention")
plt.figure(figsize=(10,7.5))
ax_fixed = plt.subplot()
plt.bar(
  range(0,len(protection_counts[protection_counts.conservation_status != "No Intervention"])),
  protection_counts[protection_counts.conservation_status != "No Intervention"].scientific_name
)
plt.ylabel("Number of Species", fontsize = 14)
plt.title("Conservation Status by Species", fontsize = 14)
ax_fixed.set_xticks(range(0,
    len(protection_counts[protection_counts.conservation_status != "No Intervention"])))
ax_fixed.set_xticklabels(protection_counts[protection_counts.conservation_status != "No Intervention"].conservation_status)
ax_fixed.tick_params(axis='both', which='major', labelsize=10)
plt.savefig("results/conversation_no_intervention_excluded.png")


#### STEP 4: Investigating Endangered Species ####
# Add extra column for estimation if species is protected
species["is_protected"] = species.conservation_status.apply(
	lambda x: True if x != "No Intervention" else False
)

# Group data by category and is_protected
category_counts = species.groupby(["category", "is_protected"])["scientific_name"].nunique().reset_index()

# Print grouped data
print("\nData grouped by category and protection status:")
# print(category_counts)
# print("\n")

# Pivot grouped data
category_pivot = category_counts.pivot(
  columns = "is_protected",
  index = "category",
  values = "scientific_name"
).reset_index()


#### STEP 7: Fix column names and calculate amount of animals being especially dangered ####
# Fix unhandy column names
category_pivot.columns = ["category", "not_protected", "protected"]

# Calculate percentage of protected animals
category_pivot["percent_protected"] = 100 * category_pivot["protected"] / (category_pivot["protected"] + category_pivot["not_protected"])

# Print Pivot
print(category_pivot)
category_pivot.to_csv("results/percent_protected.csv", sep = "\t")

# Plot percentage values for the endangered animals to bar chart
plt.figure(figsize=(10,7.5))
ax_fixed = plt.subplot()
plt.bar(
  range(0,len(category_pivot)),
  category_pivot.percent_protected
)
plt.ylim([0,100])
plt.ylabel("Species being protected [%]", fontsize = 14)
plt.title("Conservation Status by Species (Percent, per species)", fontsize = 14)
ax_fixed.set_xticks(range(0,len(category_pivot)))
ax_fixed.set_xticklabels(category_pivot.category)
ax_fixed.tick_params(axis='both', which='major', labelsize=10)
plt.savefig("results/species_protected_percent.png")

plt.show()


#### STEP 8: Performing a chi-squared test on the category values ####
def test_contingency(animal1, animal2):
    contingency_array = category_pivot[(category_pivot.category == animal1) | (category_pivot.category == animal2)].iloc[:,1:3]
    contingency = []
    for column in range(len(contingency_array.columns)-1,-1,-1):
      contingency.append(contingency_array.iloc[column,:])
    pval = chi2_contingency(contingency)[1]
    return pval

# Comparing all different animals with each other and output results
endangerment_matrix = pd.DataFrame()
endangerment_matrix["compare_group"] = category_pivot.category
endangerment_matrix_string = pd.DataFrame()
endangerment_matrix_string["compare_group"] = category_pivot.category
for row, compare_animal in enumerate(endangerment_matrix.compare_group):
    result_matrix = []
    result_matrix_string = []
    for test_animal in endangerment_matrix.compare_group:
        if test_animal == compare_animal:
            result_matrix.append("NaN")
            result_matrix_string.append("---")
        else:
            result_matrix.append(test_contingency(compare_animal,test_animal))
            if test_contingency(compare_animal,test_animal) > 0.05:
                result_matrix_string.append("n.d.")
            else:
                result_matrix_string.append("s.d.")
    endangerment_matrix[compare_animal] = result_matrix
    endangerment_matrix_string[compare_animal] = result_matrix_string
    if not row:
        total = []
    total.append(
        sum(
            [1 for endangerment_entry in endangerment_matrix_string[compare_animal] if endangerment_entry == "s.d."]
        )
    )

endangerment_matrix_string["total_significant_deviations"] = total

print("\nComparison between endangered species:")
print(endangerment_matrix)
endangerment_matrix.to_csv("results/endangerment_matrix.csv", sep = "\t")
print("\n")
print(endangerment_matrix_string)
endangerment_matrix_string.to_csv("results/endangerment_matrix_string.csv", sep = "\t")


#### STEP 10: Inspecting Observation Data ####
# Loading DataFrame for the animal data
observations = pd.read_csv("observations.csv")

# Inspection of data structure:
# scientific_name | park_name | observations
# print(species.head())


#### STEP 11: Create 'is_sheep' column in species DataFrame ####
species = pd.read_csv('species_info.csv')
species.fillna('No Intervention', inplace = True)
species['is_protected'] = species.conservation_status != 'No Intervention'

species["is_sheep"] = species.common_names.apply(
	lambda x: True if "Sheep" in x else False
)

species_is_sheep = species[species.is_sheep == True]
sheep_species = species[(species.is_sheep == True) & (species.category == "Mammal")]
print(sheep_species)
sheep_species.to_csv("results/sheep_species.csv", sep = "\t")


#### STEP 12: Merge of Sheep Species DataFrame and Observation DataFrame ####
sheep_observations = sheep_species.merge(observations)
print(sheep_observations)
sheep_observations.to_csv("results/sheep_observations.csv", sep = "\t")

# Get number of sheep observations per park, given in an aggregate
obs_by_park = sheep_observations.groupby("park_name")["observations"].sum().reset_index()
print(obs_by_park)
obs_by_park.to_csv("results/sheep_per_park.csv", sep = "\t")


#### STEP 13: Plotting Sheep Observations ####
plt.figure(figsize=(16,4))
ax = plt.subplot()
plt.bar(
  range(0,len(obs_by_park)),
  obs_by_park.observations
)
ax.set_xticks(range(0,len(obs_by_park)))
ax.set_xticklabels(obs_by_park.park_name)

plt.ylabel("Number of Observations", fontsize = 14)
plt.title("Observations of Sheep per week", fontsize = 14)
ax.tick_params(axis='both', which='major', labelsize=10)
# plt.show()
plt.savefig("results/no_of_sheep_observed.png")


#### STEP 14: Foot and Mouth Reduction Effort - Sample Size Determination ####
# define values from exercise
baseline = 15 # previous baseline
minimum_detectable_effect = 33.33 # minimum detectable effect = (-)5 %, i.e. 33.33 % of 15
sample_size_per_variant = 870 # determined by sample size calculator

# get sample sizes
def get_weeks_observing(sample_size, df, park_description):
    weeks_observing = float(sample_size) / df.at[df.loc[df['park_name'] == park_description].index[0], "observations"]
    return weeks_observing
yellowstone_weeks_observing = get_weeks_observing(890, obs_by_park, "Yellowstone National Park")
bryce_weeks_observing = get_weeks_observing(890, obs_by_park, "Bryce National Park")