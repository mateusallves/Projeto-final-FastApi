from app.data.database import Base, engine, SessionLocal
from app.models.categoria_model import Categoria
from app.models.produto_model import Produto
from app.models.contato_model import Contato



def create_tables():
	Base.metadata.create_all(bind=engine)


def seed():
	db = SessionLocal()
	try:
		# Verifica se já existem categorias
		existing = db.query(Categoria).count()
		if existing == 0:
			# categorias principais e subcategorias (como itens simples)
			categorias = [
				"Bolos",
				"Bolos de Doce de Leite",
				"Bolos de Chocolate",
				"Bolos de Frutas",
				"Bolos Folhados",
				"Bolos no Pote",
				"Bolo de Cristal de Gelatina",
				"Kit Festa",
				"Docinhos",
				"Docinhos de Festa I",
				"Docinhos de Festa II",
				"Docinhos de Festa Especiais I",
				"Docinhos de Festa Especiais II",
				"Sobremesas",
				"Pudim",
				"Cocada Brulée",
				"Mil Folhas",
				"Sobremesa na taça",
				"Tortas",
				"Banoffe",
				"Romeu e Julieta",
				"Cheesecake de Frutas vermelhas",
				"Holandesa",
				"Morango",
				"Coffee Break",
				"Mini Palha Italiana",
				"Mini Brownie",
				"Panacotta",
				"Bombons",
				"Rocamboles",
				"Salada de frutas",
				"Especiais",
				"Especiais do Mês",
			]

			cat_objs = [Categoria(nome=n) for n in categorias]
			db.add_all(cat_objs)
			db.commit()
			for c in cat_objs:
				db.refresh(c)

			# adicionar alguns produtos de exemplo
			p1 = Produto(nome="Bolo de Chocolate", descricao="Bolo de chocolate 20cm", preco=75.0, categoria_id=[c.id for c in cat_objs if c.nome=="Bolos de Chocolate"][0])
			p2 = Produto(nome="Brigadeiro", descricao="Brigadeiro tradicional", preco=2.5, categoria_id=[c.id for c in cat_objs if c.nome=="Docinhos de Festa I"][0])
			p3 = Produto(nome="Kit Petit Comitê 6 pessoas", descricao="Kit com variedades para 6 pessoas", preco=120.0, categoria_id=[c.id for c in cat_objs if c.nome=="Kit Festa"][0])
			db.add_all([p1, p2, p3])
			db.commit()
			print("Seed: categorias, produtos e kits inseridos.")
		else:
			print("Seed: já existem dados. Nenhuma ação feita.")
	finally:
		db.close()


if __name__ == "__main__":
	create_tables()
	seed()
