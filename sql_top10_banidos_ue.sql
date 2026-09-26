SELECT 
	d.nome_ingrediente,
    COUNT(f.nr_registro) AS total_produtos_comerciais_br,
    u.cluster_ia AS grupo_de_risco_kmeans
FROM
	fato_produto_formulado f
INNER JOIN
	dim_ingrediente d ON f.id_ingrediente = d.id_ingrediente
INNER JOIN
	dim_regulacao_ue u ON d.id_ingrediente = u.id_ingrediente
WHERE
	u.status_aprovacao_ue = 'Not approved'
GROUP BY
	d.nome_ingrediente, u.cluster_ia
ORDER BY
	total_produtos_comerciais_br DESC
LIMIT 10;