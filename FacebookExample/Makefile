clean_dist:
	find ./ -name '*~' -exec rm {} \; | echo 'none'
	find ./ -name '#*' -exec rm {} \; | echo 'none'
	find ./ -name '*.pyc' -exec rm {} \;
	rm sessions/*       | echo 'none'
	rm errors/*         | echo 'none'
	rm cache/*          | echo 'none'        
	rm databases/*         | echo 'none'
	tar cvf ~/Desktop/web2py.app.facebook.tar *
