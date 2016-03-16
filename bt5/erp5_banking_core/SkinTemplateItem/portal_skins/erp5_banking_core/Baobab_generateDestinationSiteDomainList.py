domain_list = []
i = 0
vault_list = context.Delivery_getVaultItemList(leaf_node=0, vault_type="site")

# get depth
depth = len(parent.getPath().split('/')[3:])

for vault in vault_list:
  if vault[0] != '':
    if len(vault[0].split('/')) == depth:      
      if depth > 1:
        path_length = len(vault[0].split('/')) - 1
        parent_path = '/'.join(parent.getPath().split('/')[-path_length:])
        if '/'.join(vault[0].split('/')[:-1]) != parent_path:
          # only add those from parent
          continue
      domain = parent.generateTempDomain(id=vault[0].split('/')[-1])
      domain.edit(title=vault[0].split('/')[-1], membership_criterion_base_category=('destination',), membership_criterion_category=('destination/%s' %(vault[1]),), domain_generator_method_id=script.id)
      i+=1
      domain_list.append(domain)

return domain_list
