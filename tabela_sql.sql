USE colonialismo_quimico;
CREATE TABLE dim_ingrediente (
	id_ingrediente INT AUTO_INCREMENT PRIMARY KEY,
    nome_ingrediente VARCHAR(255) UNIQUE NOT NULL
);