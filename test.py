LIMIT = 20000000
cfdis_download_counter = 20000000

invoices = [f"{i+1}" for i in range(1000)]

invoices = invoices[:LIMIT - cfdis_download_counter]

print(len(invoices))
print(invoices)
print(cfdis_download_counter + len(invoices))