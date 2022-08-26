CREATE TABLE IF NOT EXISTS "categories" (
	"partuid" varchar(255) NOT NULL,
	"name" varchar(255) NOT NULL,
	"alias" varchar(255) NOT NULL,
	CONSTRAINT "categories_pk" PRIMARY KEY ("partuid")
) WITH (
  OIDS=FALSE
);

CREATE TABLE IF NOT EXISTS "products" (
	"uid" varchar(255) NOT NULL,
	"title" varchar(255) NOT NULL,
	"price" varchar(255) NOT NULL,
	"descr" TEXT,
	"text" TEXT,
	"img" varchar(255) NOT NULL,
	"quantity" varchar(255) NOT NULL,
	"gallery" TEXT,
	"url" varchar(255) NOT NULL,
	"partuids" TEXT NOT NULL,
	CONSTRAINT "products_pk" PRIMARY KEY ("uid")
) WITH (
  OIDS=FALSE
);
