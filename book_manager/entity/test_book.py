from book import BookItem


class TestBookItem():
    def test_equal(self):
        # Arrange
        book1 = BookItem("title1", "url1", ["tag1"])
        book2 = BookItem("title1", "url1", ["tag1"])

        # Act
        # result = book1.__eq__(book2)
        result = book1 == book2

        # Assert
        assert result

    def test_equal_other_instance(self):
        # Arrange
        book1 = BookItem("title1", "url1", ["tag1"])
        book2 = 'BookItem("title1", "url1", ["tag2"])'

        # Act
        result = book1.__eq__(book2)

        # Assert
        assert not result

    def test_equal_different_title(self):
        # Arrange
        book1 = BookItem("title1", "url1", ["tag1"])
        book2 = BookItem("title2", "url1", ["tag1"])

        # Act
        result = book1.__eq__(book2)

        # Assert
        assert not result

    def test_equal_different_url(self):
        # Arrange
        book1 = BookItem("title1", "url1", ["tag1"])
        book2 = BookItem("title1", "url2", ["tag1"])

        # Act
        result = book1.__eq__(book2)

        # Assert
        assert not result

    def test_equal_different_tags(self):
        # Arrange
        book1 = BookItem("title1", "url1", ["tag1"])
        book2 = BookItem("title1", "url1", ["tag2", "tag3"])

        # Act
        result = book1.__eq__(book2)

        # Assert
        assert result

    def test_in(self):
        # Arrange
        book1 = BookItem("title1", "url1", ["tag1"])
        book2 = BookItem("title2", "url1", ["tag2", "tag3"])
        books = [book1, book2]

        # Act
        result = book1 in books

        # Assert
        assert result

    def test_in_false(self):
        # Arrange
        book1 = BookItem("title1", "url1", ["tag1"])
        book2 = BookItem("title2", "url1", ["tag2", "tag3"])
        book3 = BookItem("title3", "url1", ["tag2", "tag3"])
        books = [book2, book3]

        # Act
        result = book1 in books

        # Assert
        assert not result
