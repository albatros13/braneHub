package data.format

# Decision document for data format acceptability
# Usage examples:
#  opa eval -I -d data_format_acceptance.rego -i input.json "data.data.format.decision"
# Expected input shape:
#  {
#    "expected": <object matching data_format_expectations_input_schema.json>,
#    "provided": <object matching data_format_input_schema.json>
#  }

default decision = {
  "allow": false,
  "deny_reasons": [],
  "requirements": [],
  "notes": []
}

# Top-level decision assembly
decision = {
  "allow": allow,
  "deny_reasons": denies,
  "requirements": reqs,
  "notes": notes,
} {
  expected := input.expected
  provided := input.provided

  denies := collect_denies(expected, provided)
  reqs := collect_requirements(expected, provided)
  notes := collect_notes(expected, provided)
  allow := count(denies) == 0
  # If there are no denies but there are strong requirements meaning no acceptable/conditional matches,
  # we still keep allow=false if requirement severity is "blocker". We simplify by treating all reqs as non-blocking.
}

########################
# Deny rules
########################

collect_denies(expected, provided) = reasons {
  reasons := concat_arrays([
    deny_storage_category("files", expected, provided),
    deny_storage_category("databases", expected, provided),
    deny_storage_category("apis_streams", expected, provided),
    deny_storage_category("object_store", expected, provided),
    deny_delivery_methods(expected, provided),
    deny_schema_contracts(expected, provided)
  ])
}

# If provided contains any value listed in not_acceptable for a storage subcategory -> deny
deny_storage_category(kind, expected, provided) = arr {
  exp := expected.storage[kind]
  not_acceptable := array_or_empty(exp.not_acceptable)
  prov := array_or_empty(provided.storage[kind])

  violations := [v | v := prov[_]; v == not_acceptable[_]]
  count(violations) > 0
  arr := [sprintf("Storage '%v' value '%v' is not acceptable", [kind, violations[_]])]
} else = [] { true }

# If provided delivery methods contain a not_acceptable value -> deny
deny_delivery_methods(expected, provided) = arr {
  exp := expected.delivery.methods
  not_acceptable := array_or_empty(exp.not_acceptable)
  prov := array_or_empty(provided.delivery.methods)
  violations := [v | v := prov[_]; v == not_acceptable[_]]
  count(violations) > 0
  arr := [sprintf("Delivery method '%v' is not acceptable", [violations[_]])]
} else = [] { true }

# If provided schema contracts contain any that are explicitly not_acceptable -> deny
deny_schema_contracts(expected, provided) = arr {
  exp := expected.schema.contracts
  not_acceptable := array_or_empty(exp.not_acceptable)
  prov_yes := provided_schema_yes(provided)
  violations := [v | v := prov_yes[_]; v == not_acceptable[_]]
  count(violations) > 0
  arr := [sprintf("Schema contract '%v' is not acceptable", [violations[_]])]
} else = [] { true }

########################
# Requirements (non-blocking recommendations or conditions)
########################

collect_requirements(expected, provided) = reqs {
  reqs := concat_arrays([
    requirement_storage_matches("files", expected, provided),
    requirement_storage_matches("databases", expected, provided),
    requirement_storage_matches("apis_streams", expected, provided),
    requirement_storage_matches("object_store", expected, provided),
    requirement_delivery_matches(expected, provided),
    requirement_schema_matches(expected, provided)
  ])
}

# If there is no match with acceptable but there is a match with conditional -> add requirement
# If neither acceptable nor conditional match and expected lists any acceptable/conditional -> add stronger requirement
requirement_storage_matches(kind, expected, provided) = arr {
  exp := expected.storage[kind]
  acceptable := array_or_empty(exp.acceptable)
  conditional := array_or_empty(exp.conditional)

  prov := array_or_empty(provided.storage[kind])

  has_acc := intersects(prov, acceptable)
  has_cond := intersects(prov, conditional)

  some_listed := count(acceptable) > 0 or count(conditional) > 0

  has_acc == false
  has_cond == true
  arr := [sprintf("Storage '%v': permitted under conditions (%v). Ensure stated conditions are met.", [kind, concat_arr(conditional)])]
} else = arr {
  exp := expected.storage[kind]
  acceptable := array_or_empty(exp.acceptable)
  conditional := array_or_empty(exp.conditional)
  prov := array_or_empty(provided.storage[kind])

  has_acc := intersects(prov, acceptable)
  has_cond := intersects(prov, conditional)
  some_listed := count(acceptable) > 0 or count(conditional) > 0

  has_acc == false
  has_cond == false
  some_listed
  arr := [sprintf("Storage '%v': provide one of acceptable (%v) or conditional (%v) formats.", [kind, concat_arr(acceptable), concat_arr(conditional)])]
} else = [] { true }

requirement_delivery_matches(expected, provided) = arr {
  exp := expected.delivery.methods
  acceptable := array_or_empty(exp.acceptable)
  conditional := array_or_empty(exp.conditional)
  prov := array_or_empty(provided.delivery.methods)

  has_acc := intersects(prov, acceptable)
  has_cond := intersects(prov, conditional)

  has_acc == false
  has_cond == true
  arr := [sprintf("Delivery methods permitted under conditions (%v). Ensure conditions are met.", [concat_arr(conditional)])]
} else = arr {
  exp := expected.delivery.methods
  acceptable := array_or_empty(exp.acceptable)
  conditional := array_or_empty(exp.conditional)
  prov := array_or_empty(provided.delivery.methods)

  some_listed := count(acceptable) > 0 or count(conditional) > 0
  has_acc := intersects(prov, acceptable)
  has_cond := intersects(prov, conditional)

  some_listed
  has_acc == false
  has_cond == false
  arr := [sprintf("Provide one of acceptable (%v) or conditional (%v) delivery methods.", [concat_arr(acceptable), concat_arr(conditional)])]
} else = [] { true }

requirement_schema_matches(expected, provided) = arr {
  exp := expected.schema.contracts
  acceptable := array_or_empty(exp.acceptable)
  conditional := array_or_empty(exp.conditional)
  prov_yes := provided_schema_yes(provided)

  has_acc := intersects(prov_yes, acceptable)
  has_cond := intersects(prov_yes, conditional)

  has_acc == false
  has_cond == true
  arr := [sprintf("Schema contracts permitted under conditions (%v). Ensure conditions are met.", [concat_arr(conditional)])]
} else = arr {
  exp := expected.schema.contracts
  acceptable := array_or_empty(exp.acceptable)
  conditional := array_or_empty(exp.conditional)
  prov_yes := provided_schema_yes(provided)

  some_listed := count(acceptable) > 0 or count(conditional) > 0
  has_acc := intersects(prov_yes, acceptable)
  has_cond := intersects(prov_yes, conditional)

  some_listed
  has_acc == false
  has_cond == false
  arr := [sprintf("Provide one of acceptable (%v) or conditional (%v) schema contracts.", [concat_arr(acceptable), concat_arr(conditional)])]
} else = [] { true }

########################
# Notes
########################

collect_notes(expected, provided) = notes {
  notes := []
}

########################
# Helpers
########################

# Safely treat missing arrays as empty
array_or_empty(x) = arr {
  arr := x
} else = [] {
  not x
} else = [] {
  x == null
}

# set intersection predicate (true if any common element)
intersects(a, b) {
  some i, j
  a[i] == b[j]
}

# Provided schema contracts with value "Yes"
provided_schema_yes(provided) = out {
  sc := provided.schema
  names := [k | some k; sc[k] == "Yes"]
  out := names
} else = [] { true }

# Concatenate array to comma-separated string
concat_arr(arr) = s {
  s := concat(", ", [x | x := arr[_]])
}
