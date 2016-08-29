# openstack-project-generator
Sample generator for openstack new projects(Base on openstack stable/liberty version).

## Quick start
Follow those steps to generate new projects:

1. Get openstack-project-generator by command: `git clone https://github.com/hahaps/openstack-project-generator.git`.
2. Go into openstack-project-generator by command: `cd openstack-project-generator`.
3. Run command `./generate.sh -h` or `./generate.sh --help` for usage help.
4. To generate a project with only `API` service, run `./generate.sh <project_name> <project_path>` such as `./generate.sh hahaps .`.
5. To generate a project with `API` and `Manager` services, run `./generate.sh -m <manager_service_name> <project_name> <project_path>` such as `./generate.sh -m recover hahaps .`.

## Install and Run
To Install new project generated with `openstack-project-generator` for development level:
  sudo pip install -r <new_project_path>/requirements.txt -e <new_project_path>

Follow tox command will be usful for testing and generate config.sample files:
* To generate config.sample files: `tox -egenconfig`.
* To run unit test: `tox -epy27`.
* To run pep8 test: `tox -epep8`.

## Known bugs
1. When generate a new project with only `API` services and it named hahap, then `hahap-all` will run failed.

## License

   Author: Li Xipeng<lixipeng@hihuron.com>(From Beijing Huron Technology Co.Ltd)

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
