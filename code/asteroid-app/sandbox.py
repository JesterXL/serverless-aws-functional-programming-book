def sup(firstName):
    def last(lastName):
        return f"What's up {firstName} {lastName}!?"
    return last

a = sup('Jesse')
print(a)

