SELECT
	u.cluster_ia AS cluster_risco,
    COUNT(DISTINCT d.nome_ingrediente) AS qtd_ingrediente_unicos,
    COUNT(f.nr_registro) AS volume_total_produtos,
    SUM(u.risco_aquatico) AS soma_alertas_risco_aquatico
FROM
	fato_produto_formulado f
INNER JOIN
	dim_ingrediente d ON f.id_ingrediente = d.id_ingrediente
INNER JOIN
	dim_regulacao_ue u ON d.id_ingrediente = u.id_ingrediente
GROUP BY
	u.cluster_ia
ORDER BY
	cluster_risco;