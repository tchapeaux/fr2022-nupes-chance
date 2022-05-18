import json

# Load data from indivisibles
with open("indivisible_circo_with_chance.json") as f:
	data= json.loads(f.read())["features"]

data = [d["properties"] for d in data]

print(len(data), "departments") # They have 566 departments when there are 577
print("Majority =", int(len(data) / 2))

nupes = ["roussel", "melenchon", "jadot", "hidalgo"]
centre_droit = ["macron", "pecresse"]
extreme_droite = ["lepen", "zemmour", "nda"]

# Validate the input
# Does the "chance" attribute correspond to the textual explanation given on the website?
for d in data:
	sum_nupes = sum([d[key] for key in nupes])
	sum_centre_droit = sum([d[key] for key in centre_droit])
	sum_extreme_droite = sum([d[key] for key in extreme_droite])

	if (sum_nupes > sum_centre_droit and sum_nupes > sum_extreme_droite):
		assert d["chance"] == 2
	elif (sum_nupes > d["macron"] and sum_nupes > d["lepen"]):
		assert d["chance"] == 1
	else:
		assert d["chance"] == 0


# print("chance 0 =", len([d for d in data if d["chance"] == 0]))
# print("chance 1 =", len([d for d in data if d["chance"] == 1]))
# print("chance 2 =", len([d for d in data if d["chance"] == 2]))

# print("---now our own stats")

print("\nPotential 1st round wins:")
print("nupes =", len([d for d in data if sum([d[key] for key in nupes]) >= 50]))
print("centre_droit =", len([d for d in data if sum([d[key] for key in centre_droit]) >= 50]))
print("extreme_droite =", len([d for d in data if sum([d[key] for key in extreme_droite]) >= 50]))


# Simulate the elections naively
deputies = {}
deputies["nupes"] = 0
deputies["macron"] = 0
deputies["pecresse"] = 0
deputies["lepen"] = 0
deputies["zemmour"] = 0

# count tri- and quadri-partites
# (2nd round with 3 or 4 candidates)
tripartites = 0
quadripartites = 0

# preferrences for each camp (sorted)
preferences = {}
preferences["nupes"] = ["macron", "pecresse", "lepen"]
preferences["macron"] = ["pecresse", "nupes"]
preferences["pecresse"] = ["macron", "zemmour"]
preferences["lepen"] = ["zemmour", "pecresse", "macron"]
preferences["zemmour"] = ["lepen", "pecresse", "macron"]
preferences["nda"] = ["lepen", "zemmour", "pecresse", "macron"]

print("\nSimulating", len(data), "elections...")

front_republicain_count = 0

for d in data:
	sum_nupes = sum([d[key] for key in nupes])

	# check for round 1 wins
	if sum_nupes > 50:
		deputies["nupes"] += 1
	elif d["macron"] > 50:
		deputies["macron"] += 1
	elif d["pecresse"] > 50:
		deputies["pecresse"] += 1
	elif d["lepen"] > 50:
		deputies["lepen"] += 1
	elif d["zemmour"] > 50:
		deputies["zemmour"] += 1
	else:
		# If round 1 did not yield a result => simulate round 2
		round2 = []
		podium = sorted([
			(sum_nupes, "nupes"),
			(d["macron"], "macron"),
			(d["pecresse"], "pecresse"),
			(d["lepen"], "lepen"),
			(d["nda"], "nda"),
			(d["zemmour"], "zemmour"),
		])

		#print("podium round 1", podium)
		if podium[-2][0] >= 12.5:
			# If 2 candidates have more than 12.5, take all candidates meeting that treshold
			round2 = [p for p in podium if p[0] >= 12.5]
		else:
			# Otherwise, take the first 2 candidates
			round2 = [podium[-1], podium[-2]]

		# count tripartites and quadripartites (just to have the info)
		if len(round2) >= 3:
			tripartites += 1
			if len(round2) >= 4:
				quadripartites += 1

		# simulate votes transfer (naively)
		round2Votes = {}
		for candidate in [x[1] for x in round2]:
			# keep round1 vote if candidate is present in round2
			round2Votes[candidate] = sum_nupes if candidate == "nupes" else d[candidate]

		for candidate in [x[1] for x in podium if x not in round2]:
			# vote transfer based on preferences if candidate is not in round2
			for pref in preferences[candidate]:
				if pref in round2Votes:
					round2Votes[pref] += d[candidate]
					break

		round2Podium = sorted([(score, cand) for cand, score in round2Votes.items()])
		#print("podium round 2", round2Podium)

		# Naive winner : better-placed
		winner = round2Podium[-1][1]

		# Simulate Front Republicain
		# if an XD candidate can win at round 2, votes will focus on the better-placed republican candidate
		front_repub_candidates = ["nupes", "macron", "pecresse"]
		if (winner in extreme_droite and any([c in round2Votes for c in front_repub_candidates])):
			front_score = d["macron"]  + sum_nupes  + d["pecresse"] 
			if front_score > round2Podium[-1][0]:
				front_republicain_count += 1
				winner = [c[1] for c in round2Podium if c[1] in ["nupes", "macron", "pecresse"]][0]

		#print("WINNER=", winner)
		deputies[winner] += 1

print("\n= RESULTS =")

print("\ttripartites count", tripartites)
print("\tquadripartites count", quadripartites)
print("\tfront republicain deputies:", front_republicain_count)

print("\nDeputies count", deputies)
