SELECT
	f.titular_registro AS empresa_fabricante,
    COUNT(f.nr_registro) AS total_produtos_alto_perigo
FROM
	fato_produto_formulado f
INNER JOIN
	dim_regulacao_ue u ON f.id_ingrediente = u.id_ingrediente
WHERE
	u.risco_cancer_mutacao = 1 OR u.risco_reprodutivo = 1
GROUP BY
	f.titular_registro
ORDER BY
	total_produtos_alto_perigo DESC
LIMIT 10;