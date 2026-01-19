package simple.onboarding_plus

# Extended policy that accounts for variations in region description.
# It uses a mapping of common variations to their canonical region names.

default allow = false

# Canonical mapping (simplified for this exercise, usually passed via data)
region_mapping := {
    "United States": ["United States", "USA", "U.S.", "America", "California, USA", "New York", "US citizen", "US", "USA"],
    "United Kingdom": ["United Kingdom", "UK", "Great Britain", "England", "London, UK", "Britain", "U.K.", "GB"],
    "European Union": ["European Union", "EU", "Europe", "EU resident", "EU citizen", "Based in the EU"],
    "Germany": ["Germany", "DE", "Deutschland", "Berlin", "Hamburg, Germany", "German resident"],
    "Netherlands": ["Netherlands", "NL", "Holland", "Amsterdam", "The Netherlands", "Dutch"],
    # ... can be extended with more from region_options.json
}

allow {
    some acceptable_loc in input.acceptable_locations
    is_match(input.location, acceptable_loc)
}

# Match if exact
is_match(loc, target) {
    loc == target
}

# Match if loc is a known variation of target
is_match(loc, target) {
    variations := region_mapping[target]
    variations[_] == loc
}

# Match if target is a substring or vice versa (fuzzy-ish logic for Rego)
is_match(loc, target) {
    contains(lower(loc), lower(target))
}
is_match(loc, target) {
    contains(lower(target), lower(loc))
}

decision := {"allow": allow}
