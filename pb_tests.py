"""Tests for pub"""
import pb

blog = pb.Pub()

""" test all posts"""
#blog.all_posts()

""" test if rebuild index can get all the content from the posts """
blog.rebuild_index()
