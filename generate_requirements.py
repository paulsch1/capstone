import pkg_resources

def generate_requirements():
    # Get a list of installed packages and their versions
    installed_packages = pkg_resources.working_set
    # Sort packages alphabetically
    sorted_packages = sorted(["{}=={}".format(p.key, p.version) for p in installed_packages])

    # Write the requirements to a text file
    with open('requirements.txt', 'w') as file:
        file.write('\n'.join(sorted_packages))

if __name__ == "__main__":
    generate_requirements()
    print("Requirements generated successfully.")
