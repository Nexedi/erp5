sensor_reference = reference.split('.')[0]
data_product_reference = reference.split('.')[1]
return {'resource_reference' : data_product_reference,
        'specialise_reference': sensor_reference,
        'reference': sensor_reference   }
