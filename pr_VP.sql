--
-- PostgreSQL database dump
--

-- Dumped from database version 16.1
-- Dumped by pg_dump version 16.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: statistics_sample; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.statistics_sample (
    id_statistics integer NOT NULL,
    date date,
    variable character varying(50) NOT NULL,
    min integer NOT NULL,
    max integer NOT NULL
);


ALTER TABLE public.statistics_sample OWNER TO postgres;

--
-- Name: statistics_sample_id_statistics_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.statistics_sample_id_statistics_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.statistics_sample_id_statistics_seq OWNER TO postgres;

--
-- Name: statistics_sample_id_statistics_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.statistics_sample_id_statistics_seq OWNED BY public.statistics_sample.id_statistics;


--
-- Name: statistics_sample id_statistics; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.statistics_sample ALTER COLUMN id_statistics SET DEFAULT nextval('public.statistics_sample_id_statistics_seq'::regclass);


--
-- Data for Name: statistics_sample; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.statistics_sample (id_statistics, date, variable, min, max) FROM stdin;
1	2023-11-09	ff -	834	2293
2	2023-11-09	fl	824	2276
3	2023-11-09	pt	819	2270
4	2023-11-09	lf -	0	6
5	2023-11-09	ll	0	6
6	2023-11-09	tp -	0	3
7	2023-11-09	tt	0	3
8	2023-11-09	ff.lit -	0	37
9	2023-11-09	fl.lit	0	37
10	2023-11-09	pt.lit	0	32
11	2023-11-09	lf.lit -	0	18
12	2023-11-09	ll.lit	0	18
13	2023-11-09	tp.lit -	0	3
14	2023-11-09	tt.lit	0	3
15	2023-11-10	ff -	1155	2044
16	2023-11-10	fl	1262	2009
17	2023-11-10	pt	1261	2007
18	2023-11-10	lf -	0	171
19	2023-11-10	ll	0	171
20	2023-11-10	tp -	0	52
21	2023-11-10	tt	0	52
22	2023-11-10	ff.lit -	0	3
23	2023-11-10	fl.lit	0	3
24	2023-11-10	pt.lit	0	3
25	2023-11-10	lf.lit -	0	2
26	2023-11-10	ll.lit	0	2
27	2023-11-10	tp.lit -	0	1
28	2023-11-10	tt.lit	0	1
29	2023-11-11	ff -	0	1137
30	2023-11-11	fl	100	1236
31	2023-11-11	pt	119	1235
32	2023-11-11	lf -	0	112
33	2023-11-11	ll	0	112
34	2023-11-11	tp -	0	40
35	2023-11-11	tt	0	32
36	2023-11-11	ff.lit -	0	0
37	2023-11-11	fl.lit	0	0
38	2023-11-11	pt.lit	0	0
39	2023-11-11	lf.lit -	0	6
40	2023-11-11	ll.lit	0	5
41	2023-11-11	tp.lit -	0	1
42	2023-11-11	tt.lit	0	1
43	2023-11-12	ff -	0	0
44	2023-11-12	fl	100	100
45	2023-11-12	pt	119	119
46	2023-11-12	lf -	0	1
47	2023-11-12	ll	0	1
48	2023-11-12	tp -	0	1
49	2023-11-12	tt	0	1
50	2023-11-12	ff.lit -	0	0
51	2023-11-12	fl.lit	0	0
52	2023-11-12	pt.lit	0	0
53	2023-11-12	lf.lit -	0	3
54	2023-11-12	ll.lit	0	2
55	2023-11-12	tp.lit -	0	3
56	2023-11-12	tt.lit	0	3
57	2023-11-13	ff -	0	225
58	2023-11-13	fl	0	201
59	2023-11-13	pt	0	201
60	2023-11-13	lf -	0	13
61	2023-11-13	ll	0	4
62	2023-11-13	tp -	0	5
63	2023-11-13	tt	0	3
64	2023-11-13	ff.lit -	0	25
65	2023-11-13	fl.lit	0	25
66	2023-11-13	pt.lit	0	22
67	2023-11-13	lf.lit -	0	4
68	2023-11-13	ll.lit	0	4
69	2023-11-13	tp.lit -	0	0
70	2023-11-13	tt.lit	0	0
\.


--
-- Name: statistics_sample_id_statistics_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.statistics_sample_id_statistics_seq', 70, true);


--
-- Name: statistics_sample statistics_sample_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.statistics_sample
    ADD CONSTRAINT statistics_sample_pkey PRIMARY KEY (id_statistics);


--
-- PostgreSQL database dump complete
--

