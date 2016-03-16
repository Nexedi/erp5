var = context.getVariationText() 
dest_var = var.replace("cancelled", "retired")
dest_var = dest_var.replace("mutilated", "retired")
dest_var = dest_var.replace("error", "retired")
return dest_var
